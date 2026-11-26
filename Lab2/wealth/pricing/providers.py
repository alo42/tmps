"""
Market prices (DIP from Lab 1).

The calculator depends on the `PriceProvider` abstraction only. Concrete
providers are created by a `MarketDataSource` (see sources.py).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict


class PriceProvider(ABC):

    @abstractmethod
    def get_price(self, symbol: str) -> Decimal:
        """Current unit price of `symbol` in the base currency (EUR)."""


class MockPriceProvider(PriceProvider):
    """Deterministic prices for the class demo and the unit tests."""

    def __init__(self, prices: Dict[str, Decimal]):
        self._prices = dict(prices)
        self.calls = 0  # lets the tests prove that caching works

    def get_price(self, symbol: str) -> Decimal:
        self.calls += 1
        if symbol not in self._prices:
            raise KeyError("No mock price configured for %r" % symbol)
        return self._prices[symbol]


class ApiPriceProvider(PriceProvider):
    """
    The live implementation. Deliberately a stub: the project must run with no
    network and no third-party packages. Wire a quotes endpoint in here.
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self._api_key = api_key

    def get_price(self, symbol: str) -> Decimal:
        raise NotImplementedError("Connect %s to a live quotes endpoint" % self.base_url)


class CachingPriceProvider(PriceProvider):
    """
    DECORATOR on the provider side: is a PriceProvider and wraps one, adding
    a per-session cache without modifying the provider it wraps.
    """

    def __init__(self, inner: PriceProvider):
        self.inner = inner
        self._cache: Dict[str, Decimal] = {}

    def get_price(self, symbol: str) -> Decimal:
        if symbol not in self._cache:
            self._cache[symbol] = self.inner.get_price(symbol)
        return self._cache[symbol]
