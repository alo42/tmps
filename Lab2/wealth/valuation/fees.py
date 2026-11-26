"""
DECORATOR - selling costs layered onto any portfolio component.

A decorator *is* a `PortfolioComponent` and *wraps* one, so it can be used
anywhere a holding or a group is expected. Decorators stack, and the order of
stacking is the order in which the costs are applied:

    FixedFee(PercentageFee(btc, "0.01"), "15")   ->  value * 0.99 - 15

None of the asset classes were modified to support this.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Dict, Iterator, List, Sequence, Tuple, Type

from wealth.assets.component import GroupPath, PortfolioComponent
from wealth.money import ZERO, Number, to_decimal

if TYPE_CHECKING:
    from wealth.assets.base import Asset
    from wealth.pricing.providers import PriceProvider


class ValuationDecorator(PortfolioComponent):
    """Base decorator: forwards every call to the wrapped component."""

    def __init__(self, inner: PortfolioComponent, label: str):
        self._inner = inner
        self.label = label

    @property
    def inner(self) -> PortfolioComponent:
        return self._inner

    @property
    def name(self) -> str:
        return self._inner.name

    def market_value(self, prices: PriceProvider) -> Decimal:
        return self._inner.market_value(prices)

    def walk(self, path: GroupPath = ()) -> Iterator[Tuple[GroupPath, Asset]]:
        return self._inner.walk(path)

    def outline(self, depth: int = 0) -> Iterator[Tuple[int, PortfolioComponent]]:
        return self._inner.outline(depth)

    def costs(self) -> List[str]:
        """Labels of every cost in the chain, innermost first."""
        inner = self._inner.costs() if isinstance(self._inner, ValuationDecorator) else []
        return inner + [self.label]


class PercentageFee(ValuationDecorator):
    """A fee proportional to value: brokerage commission, exchange fee."""

    def __init__(self, inner: PortfolioComponent, rate: Number, label: str = ""):
        self.rate = to_decimal(rate)
        if not ZERO <= self.rate < 1:
            raise ValueError("fee rate must be in [0, 1), got %s" % self.rate)
        super().__init__(inner, label or "fee %s%%" % (self.rate * 100).normalize())

    def market_value(self, prices: PriceProvider) -> Decimal:
        value = self._inner.market_value(prices)
        return value - value * self.rate


class FixedFee(ValuationDecorator):
    """A flat fee: notary, network withdrawal. Proceeds never go below zero."""

    def __init__(self, inner: PortfolioComponent, amount: Number, label: str = ""):
        self.amount = to_decimal(amount)
        if self.amount < 0:
            raise ValueError("fixed fee cannot be negative")
        super().__init__(inner, label or "fee %s" % self.amount)

    def market_value(self, prices: PriceProvider) -> Decimal:
        return max(self._inner.market_value(prices) - self.amount, ZERO)


FeeRule = Tuple[Type[ValuationDecorator], str, str]  # (decorator, amount, label)


class LiquidationPolicy:
    """
    Configuration, not behaviour: which decorators wrap which kind of asset.
    Changing fees means editing data here - never an asset class.
    """

    def __init__(self, rules: Dict[str, Sequence[FeeRule]]):
        self._rules = {kind: list(steps) for kind, steps in rules.items()}

    def wrap(self, asset: Asset) -> PortfolioComponent:
        component: PortfolioComponent = asset
        for decorator, amount, label in self._rules.get(asset.kind, ()):
            component = decorator(component, amount, label)
        return component

    def describe(self) -> List[Tuple[str, str]]:
        return [(kind, label) for kind, steps in sorted(self._rules.items())
                for _, _, label in steps]

    @classmethod
    def default(cls) -> LiquidationPolicy:
        """Illustrative costs of selling everything today."""
        return cls({
            "stock": [(PercentageFee, "0.005", "brokerage 0.5%")],
            "crypto": [(PercentageFee, "0.01", "exchange fee 1%"),
                       (FixedFee, "15", "withdrawal fee EUR 15")],
            "real_estate": [(FixedFee, "2550", "estate agent 3% of appraisal"),
                            (FixedFee, "1500", "notary and registry")],
        })

    @classmethod
    def none(cls) -> LiquidationPolicy:
        return cls({})
