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
class RealEstate(Asset):
    kind: ClassVar[str] = "real_estate"
    appraised_value: Decimal = Decimal("0")
    mortgage_balance: Decimal = Decimal("0")

    def market_value(self, prices: PriceProvider) -> Decimal:
        # Equity, not gross value.
        return (self.appraised_value - self.mortgage_balance) * self.quantity

    @property
    def details(self) -> Dict[str, str]:
        return {
            "appraised_value": str(self.appraised_value),
            "mortgage_balance": str(self.mortgage_balance),
        }
