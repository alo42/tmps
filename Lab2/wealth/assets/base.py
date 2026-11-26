"""
COMPOSITE - Leaf.

`Asset` is a single holding. It is also the OCP extension point from Lab 1:
every concrete asset type values itself, so new types are added as new
modules without editing the calculator, the repository or the exporters.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, fields as dataclass_fields
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar, Dict, Iterator, Tuple

from wealth.assets.component import GroupPath, PortfolioComponent

if TYPE_CHECKING:
    from wealth.pricing.providers import PriceProvider


@dataclass
class Asset(PortfolioComponent):
    symbol: str
    quantity: Decimal

    #: Stable identifier used for persistence, policies and reporting.
    kind: ClassVar[str] = "asset"

    @property
    def name(self) -> str:
        return self.symbol

    @abstractmethod
    def market_value(self, prices: PriceProvider) -> Decimal:
        """Current value of this holding. Each subclass decides *how*."""

    def walk(self, path: GroupPath = ()) -> Iterator[Tuple[GroupPath, Asset]]:
        yield path, self

    @property
    def details(self) -> Dict[str, str]:
        """Type-specific fields to persist. Overridden by subclasses."""
        return {}

    @classmethod
    def from_details(cls, symbol: str, quantity: str,
                     details: Dict[str, str]) -> Asset:
        """
        Rebuilds an asset from a stored row. Field types are read from the
        dataclass annotations, so a new subclass with new Decimal fields is
        restored correctly without any registry edit.
        """
        kwargs: Dict[str, object] = {}
        for field in dataclass_fields(cls):
            if field.name in details:
                raw = details[field.name]
                kwargs[field.name] = Decimal(raw) if "Decimal" in str(field.type) else raw
        return cls(symbol=symbol, quantity=Decimal(quantity), **kwargs)
