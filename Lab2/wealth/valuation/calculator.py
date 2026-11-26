"""
Financial calculations (SRP from Lab 1). Pure arithmetic: no SQL, no files.

Thanks to Composite the calculator accepts any `PortfolioComponent` - one
holding or a whole tree - and thanks to DIP it only knows `PriceProvider`.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from wealth.assets.component import PortfolioComponent
from wealth.money import ZERO, money
from wealth.pricing.providers import PriceProvider
from wealth.valuation.fees import LiquidationPolicy


@dataclass(frozen=True)
class Position:
    """One valued holding: the calculator's output, the exporters' input."""

    group: str
    symbol: str
    kind: str
    quantity: Decimal
    value: Decimal       # market value today
    net_value: Decimal   # what selling it would actually return

    @property
    def selling_cost(self) -> Decimal:
        return self.value - self.net_value


class PortfolioCalculator:

    def __init__(self, prices: PriceProvider):
        self._prices = prices

    def value_positions(self, portfolio: PortfolioComponent,
                        policy: Optional[LiquidationPolicy] = None) -> List[Position]:
        policy = policy or LiquidationPolicy.none()
        positions = []
        for path, asset in portfolio.walk():
            positions.append(Position(
                group="/".join(path[1:]),
                symbol=asset.symbol,
                kind=asset.kind,
                quantity=asset.quantity,
                value=money(asset.market_value(self._prices)),
                net_value=money(policy.wrap(asset).market_value(self._prices)),
            ))
        return positions

    @staticmethod
    def net_worth(positions: Iterable[Position]) -> Decimal:
        return money(sum((p.value for p in positions), ZERO))

    @staticmethod
    def liquidation_value(positions: Iterable[Position]) -> Decimal:
        return money(sum((p.net_value for p in positions), ZERO))

    def breakdown(self, portfolio: PortfolioComponent) -> List[Tuple[int, str, Decimal]]:
        """(depth, group name, value) for every group: the Composite at work."""
        return [(depth, group.name, money(group.market_value(self._prices)))
                for depth, group in portfolio.outline()]

    @classmethod
    def allocation_by_kind(cls, positions: Sequence[Position]) -> Dict[str, Decimal]:
        total = cls.net_worth(positions)
        if total == 0:
            return {}
        totals: Dict[str, Decimal] = {}
        for p in positions:
            totals[p.kind] = totals.get(p.kind, ZERO) + p.value
        return {kind: money(value / total * 100) for kind, value in totals.items()}
