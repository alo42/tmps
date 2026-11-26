"""
FACTORY METHOD - classic GoF form.

`MarketDataSource` is the Creator. Its factory method, `create_provider()`,
is abstract; each ConcreteCreator decides which `PriceProvider` (the Product)
to instantiate. The creator's own operation, `provider()`, uses the factory
method without ever naming a concrete provider class.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Optional

from wealth.pricing.providers import (ApiPriceProvider, CachingPriceProvider,
                                      MockPriceProvider, PriceProvider)

DEMO_PRICES: Dict[str, Decimal] = {
    "AAPL": Decimal("214.50"),
    "MSFT": Decimal("432.10"),
    "VWCE": Decimal("118.40"),
    "BTC": Decimal("61250.00"),
    "ETH": Decimal("2980.75"),
}


class MarketDataSource(ABC):
    """Creator."""

    def __init__(self) -> None:
        self._provider: Optional[PriceProvider] = None

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable name shown on the dashboard."""

    @abstractmethod
    def create_provider(self) -> PriceProvider:
        """The factory method. Subclasses choose the concrete product."""

    def provider(self) -> PriceProvider:
        """
        The operation built on the factory method: creates the provider once
        per session and always wraps it in a cache, whatever its type.
        """
        if self._provider is None:
            self._provider = CachingPriceProvider(self.create_provider())
        return self._provider


class DemoMarketData(MarketDataSource):
    """ConcreteCreator for the offline class demo."""

    @property
    def description(self) -> str:
        return "mock prices (offline demo)"

    def create_provider(self) -> PriceProvider:
        return MockPriceProvider(DEMO_PRICES)


class LiveMarketData(MarketDataSource):
    """ConcreteCreator for production."""

    def __init__(self, base_url: str, api_key: str):
        super().__init__()
        self._base_url = base_url
        self._api_key = api_key

    @property
    def description(self) -> str:
        return "live quotes from %s" % self._base_url

    def create_provider(self) -> PriceProvider:
        return ApiPriceProvider(self._base_url, self._api_key)
