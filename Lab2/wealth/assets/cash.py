from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar, Dict

from wealth.assets.base import Asset
from wealth.assets.factory import AssetFactory

if TYPE_CHECKING:
    from wealth.pricing.providers import PriceProvider


@AssetFactory.register
@dataclass
class CashSavings(Asset):
    """Cash is worth its balance; it never asks the price provider."""

    kind: ClassVar[str] = "cash"
    annual_rate: Decimal = Decimal("0")

    def market_value(self, prices: PriceProvider) -> Decimal:
        return self.quantity

    @property
    def details(self) -> Dict[str, str]:
        return {"annual_rate": str(self.annual_rate)}
