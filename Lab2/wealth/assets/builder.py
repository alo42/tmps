"""
BUILDER - assembles a validated portfolio tree step by step.

`PortfolioBuilder` (the builder) exposes a fluent API in which every step
returns `self`; `PortfolioDirector` (the director) knows which sequence of
steps produces each named portfolio. The product is an `AssetGroup` tree.
"""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional, Set

from wealth.assets.base import Asset
from wealth.assets.cash import CashSavings
from wealth.assets.crypto import Crypto
from wealth.assets.group import AssetGroup
from wealth.assets.real_estate import RealEstate
from wealth.assets.stock import Stock
from wealth.money import Number, to_decimal


class BuilderError(ValueError):
    """Raised when the requested portfolio would be invalid."""


class PortfolioBuilder:

    def __init__(self, name: str = "Net worth"):
        self._name = name
        self._reset()

    def _reset(self) -> None:
        self._root = AssetGroup(self._name)
        self._stack: List[AssetGroup] = [self._root]
        self._symbols: Set[str] = set()

    # --- structure ---------------------------------------------------------

    def group(self, name: str) -> PortfolioBuilder:
        """Opens a nested group; following holdings go inside it until end()."""
        child = AssetGroup(name)
        self._stack[-1].add(child)
        self._stack.append(child)
        return self

    def end(self) -> PortfolioBuilder:
        """Closes the innermost open group."""
        if len(self._stack) == 1:
            raise BuilderError("end() called with no open group")
        self._stack.pop()
        return self

    # --- holdings ----------------------------------------------------------

    def stock(self, symbol: str, quantity: Number,
              exchange: str = "NASDAQ") -> PortfolioBuilder:
        return self._add(Stock(symbol, self._quantity(symbol, quantity), exchange))

    def crypto(self, symbol: str, quantity: Number,
               wallet: str = "exchange") -> PortfolioBuilder:
        return self._add(Crypto(symbol, self._quantity(symbol, quantity), wallet))

    def cash(self, label: str, balance: Number,
             annual_rate: Number = "0") -> PortfolioBuilder:
        return self._add(CashSavings(label, self._quantity(label, balance),
                                     to_decimal(annual_rate)))

    def real_estate(self, label: str, appraised_value: Number,
                    mortgage_balance: Number = "0") -> PortfolioBuilder:
        appraised = to_decimal(appraised_value)
        mortgage = to_decimal(mortgage_balance)
        if mortgage > appraised:
            raise BuilderError("%s: mortgage exceeds appraised value" % label)
        return self._add(RealEstate(label, Decimal("1"), appraised, mortgage))

    # --- product -----------------------------------------------------------

    def build(self) -> AssetGroup:
        """Validates and returns the finished tree, then resets for reuse."""
        if len(self._stack) != 1:
            raise BuilderError("group %r was never closed with end()"
                               % self._stack[-1].name)
        if not self._symbols:
            raise BuilderError("a portfolio needs at least one holding")
        product = self._root
        self._reset()
        return product

    # --- validation helpers -------------------------------------------------

    def _add(self, asset: Asset) -> PortfolioBuilder:
        if asset.symbol in self._symbols:
            raise BuilderError("duplicate holding %r" % asset.symbol)
        self._symbols.add(asset.symbol)
        self._stack[-1].add(asset)
        return self

    @staticmethod
    def _quantity(symbol: str, value: Number) -> Decimal:
        quantity = to_decimal(value)
        if quantity < 0:
            raise BuilderError("%s: quantity cannot be negative" % symbol)
        return quantity


class PortfolioDirector:
    """BUILDER - Director: owns the recipes, delegates construction."""

    def __init__(self, builder: Optional[PortfolioBuilder] = None):
        self._builder = builder or PortfolioBuilder()

    def demo_portfolio(self) -> AssetGroup:
        """The Lab 1 holdings, now organised into accounts."""
        return (self._builder
                .group("Investments")
                    .group("Stocks")
                        .stock("AAPL", "12")
                        .stock("MSFT", "5")
                    .end()
                    .group("Crypto")
                        .crypto("BTC", "0.35", wallet="ledger")
                        .crypto("ETH", "4.2")
                    .end()
                .end()
                .group("Savings")
                    .cash("EUR-SAVINGS", "7500", annual_rate="0.0325")
                .end()
                .group("Property")
                    .real_estate("FLAT-CHISINAU", appraised_value="85000",
                                 mortgage_balance="41000")
                .end()
                .build())

    def starter_portfolio(self) -> AssetGroup:
        """A second recipe built from the same steps: first job, first ETF."""
        return (self._builder
                .group("Savings")
                    .cash("EMERGENCY-FUND", "3000", annual_rate="0.03")
                .end()
                .group("Investments")
                    .stock("VWCE", "10", exchange="XETRA")
                .end()
                .build())
