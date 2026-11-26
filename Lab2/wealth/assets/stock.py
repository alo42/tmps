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
class Stock(Asset):
    kind: ClassVar[str] = "stock"
    exchange: str = "NASDAQ"

    def market_value(self, prices: PriceProvider) -> Decimal:
        return self.quantity * prices.get_price(self.symbol)

    @property
    def details(self) -> Dict[str, str]:
        return {"exchange": self.exchange}
