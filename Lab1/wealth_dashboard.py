"""
Personal Wealth Dashboard & Multi-Asset Portfolio Tracker
=========================================================

A single-file skeleton demonstrating three SOLID principles:

  SRP  - persistence, calculation and exporting live in three separate classes.
  OCP  - new asset types plug in through the `Asset` abstraction; the
         calculator and the exporters are never edited to support them.
  DIP  - the calculator depends on the `PriceProvider` abstraction, not on a
         concrete HTTP client, so a mock provider can be injected for a demo.

Standard library only. Run with:  python3 wealth_dashboard.py
"""

from __future__ import annotations

import csv
import json
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields as dataclass_fields
from decimal import Decimal, ROUND_HALF_UP
from typing import ClassVar, Dict, Iterable, List, Sequence, Type

CENTS = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    """Round a raw Decimal to 2 places. Money is never a float."""
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# 1. DEPENDENCY INVERSION PRINCIPLE (DIP)
# ---------------------------------------------------------------------------
# The high-level policy (PortfolioCalculator) must not depend on a low-level
# detail (an HTTP API client). Both depend on this abstraction instead.


class PriceProvider(ABC):
    """Abstraction: 'something that can tell me the price of a symbol'."""

    @abstractmethod
    def get_price(self, symbol: str) -> Decimal:
        """Return the current unit price of `symbol` in the base currency."""
        raise NotImplementedError


class MockPriceProvider(PriceProvider):
    """DIP in action: deterministic prices. Safe for the live class demo."""

    def __init__(self, prices: Dict[str, Decimal]):
        self._prices = prices

    def get_price(self, symbol: str) -> Decimal:
        if symbol not in self._prices:
            raise KeyError("No mock price configured for %r" % symbol)
        return self._prices[symbol]


class ApiPriceProvider(PriceProvider):
    """
    DIP in action: the real implementation, swapped in without touching a
    single line of PortfolioCalculator.

    Left as a stub on purpose - no external dependencies are required to run
    this project. Fill in `get_price` with urllib/requests against the API of
    your choice (e.g. a quotes endpoint) when you are ready.
    """

    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url
        self._api_key = api_key

    def get_price(self, symbol: str) -> Decimal:
        raise NotImplementedError("Wire up the live quotes endpoint here.")


class CachingPriceProvider(PriceProvider):
    """
    Bonus: a decorator over any other provider. It *is* a PriceProvider and it
    *uses* a PriceProvider, so caching is added by composition - no existing
    class is modified (OCP), and the calculator cannot tell the difference
    because it only ever sees the interface (DIP).
    """

    def __init__(self, inner: PriceProvider):
        self._inner = inner
        self._cache: Dict[str, Decimal] = {}

    def get_price(self, symbol: str) -> Decimal:
        if symbol not in self._cache:
            self._cache[symbol] = self._inner.get_price(symbol)
        return self._cache[symbol]


# ---------------------------------------------------------------------------
# 2. OPEN/CLOSED PRINCIPLE (OCP)
# ---------------------------------------------------------------------------
# Every asset knows how to value *itself*. Adding Real Estate, Bonds or a
# Pension fund means adding a subclass - the calculator stays closed for
# modification but the system stays open for extension.

ASSET_REGISTRY: Dict[str, Type["Asset"]] = {}


def register_asset(cls: Type["Asset"]) -> Type["Asset"]:
    """Registers an asset type so the repository can rebuild it from a row."""
    ASSET_REGISTRY[cls.kind] = cls
    return cls


@dataclass
class Asset(ABC):
    """Abstraction over anything that contributes to net worth."""

    symbol: str
    quantity: Decimal

    #: Stable identifier used for persistence and for grouping in reports.
    kind: ClassVar[str] = "asset"

    @abstractmethod
    def market_value(self, prices: PriceProvider) -> Decimal:
        """Current value of this holding. Subclasses decide *how*."""
        raise NotImplementedError

    @property
    def details(self) -> Dict[str, str]:
        """
        Extra, type-specific fields the repository should persist. Overridden
        by subclasses; the repository stores whatever it is handed, so new
        asset types need no schema change.
        """
        return {}

    @classmethod
    def from_details(cls, symbol: str, quantity: str,
                     details: Dict[str, str]) -> "Asset":
        """
        Rebuilds an asset from its stored row. Field types are read off the
        dataclass annotations, so a new subclass with new Decimal fields is
        restored correctly without editing the repository (OCP).
        """
        kwargs: Dict[str, object] = {}
        for field in dataclass_fields(cls):
            if field.name in details:
                raw = details[field.name]
                kwargs[field.name] = (
                    Decimal(raw) if "Decimal" in str(field.type) else raw
                )
        return cls(symbol=symbol, quantity=Decimal(quantity), **kwargs)


@register_asset
@dataclass
class Stock(Asset):
    kind: ClassVar[str] = "stock"
    exchange: str = "NASDAQ"

    def market_value(self, prices: PriceProvider) -> Decimal:
        return self.quantity * prices.get_price(self.symbol)

    @property
    def details(self) -> Dict[str, str]:
        return {"exchange": self.exchange}


@register_asset
@dataclass
class Crypto(Asset):
    kind: ClassVar[str] = "crypto"
    wallet: str = "exchange"

    def market_value(self, prices: PriceProvider) -> Decimal:
        return self.quantity * prices.get_price(self.symbol)

    @property
    def details(self) -> Dict[str, str]:
        return {"wallet": self.wallet}


@register_asset
@dataclass
class CashSavings(Asset):
    """
    Note how this subclass ignores the price provider entirely: cash is worth
    its balance. The calculator does not care - that is the point of OCP.
    """

    kind: ClassVar[str] = "cash"
    annual_rate: Decimal = Decimal("0")

    def market_value(self, prices: PriceProvider) -> Decimal:
        return self.quantity

    @property
    def details(self) -> Dict[str, str]:
        return {"annual_rate": str(self.annual_rate)}


# ---------------------------------------------------------------------------
# 3. SINGLE-RESPONSIBILITY PRINCIPLE (SRP) - responsibility #1: persistence
# ---------------------------------------------------------------------------
# This class talks to the database. It does no arithmetic and no formatting.


class AssetRepository:
    """Owns storage and retrieval of assets. One reason to change: the DB."""

    def __init__(self, db_path: str = ":memory:"):
        self._conn = sqlite3.connect(db_path)
        self._create_schema()

    def _create_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS assets (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                kind     TEXT    NOT NULL,
                symbol   TEXT    NOT NULL,
                quantity TEXT    NOT NULL,  -- Decimal stored as text
                details  TEXT    NOT NULL   -- type-specific fields as JSON
            )
            """
        )
        self._conn.commit()

    def add(self, asset: Asset) -> None:
        self._conn.execute(
            "INSERT INTO assets (kind, symbol, quantity, details) VALUES (?, ?, ?, ?)",
            (asset.kind, asset.symbol, str(asset.quantity), json.dumps(asset.details)),
        )
        self._conn.commit()

    def add_many(self, assets: Iterable[Asset]) -> None:
        for asset in assets:
            self.add(asset)

    def list_all(self) -> List[Asset]:
        rows = self._conn.execute(
            "SELECT kind, symbol, quantity, details FROM assets ORDER BY id"
        ).fetchall()
        return [self._to_asset(row) for row in rows]

    @staticmethod
    def _to_asset(row: Sequence[str]) -> Asset:
        # OCP: the repository never names Stock/Crypto/Cash - it looks the
        # class up in the registry and lets the class rebuild itself, so a new
        # asset type needs no edit here.
        kind, symbol, quantity, details = row
        asset_cls = ASSET_REGISTRY.get(kind)
        if asset_cls is None:
            raise ValueError("Unknown asset kind in database: %r" % kind)
        return asset_cls.from_details(symbol, quantity, json.loads(details))

    def close(self) -> None:
        self._conn.close()


# ---------------------------------------------------------------------------
# SRP - responsibility #2: financial calculations
# ---------------------------------------------------------------------------
# Pure arithmetic. No SQL, no file I/O, no printing.


@dataclass(frozen=True)
class Position:
    """A valued holding: the calculator's output, the exporter's input."""

    symbol: str
    kind: str
    quantity: Decimal
    value: Decimal


class PortfolioCalculator:
    """
    Values a portfolio. DIP: it receives a PriceProvider through its
    constructor and only ever calls the interface method `get_price`.
    """

    def __init__(self, prices: PriceProvider):
        self._prices = prices

    def value_positions(self, assets: Iterable[Asset]) -> List[Position]:
        # No isinstance() checks and no if/elif chain over asset types: each
        # asset values itself (polymorphism is what makes OCP possible).
        return [
            Position(
                symbol=asset.symbol,
                kind=asset.kind,
                quantity=asset.quantity,
                value=money(asset.market_value(self._prices)),
            )
            for asset in assets
        ]

    def net_worth(self, positions: Iterable[Position]) -> Decimal:
        return money(sum((p.value for p in positions), Decimal("0")))

    def allocation_by_kind(self, positions: Sequence[Position]) -> Dict[str, Decimal]:
        """Percentage of total net worth held in each asset class."""
        total = self.net_worth(positions)
        if total == 0:
            return {}
        totals: Dict[str, Decimal] = {}
        for position in positions:
            totals[position.kind] = totals.get(position.kind, Decimal("0")) + position.value
        return {kind: money(value / total * 100) for kind, value in totals.items()}


# ---------------------------------------------------------------------------
# SRP - responsibility #3: exporting / reporting
# ---------------------------------------------------------------------------
# File formats change far more often than valuation rules do, so they live
# behind their own abstraction (OCP again: add a format, edit nothing).


class PortfolioExporter(ABC):
    @abstractmethod
    def export(self, positions: Sequence[Position], path: str) -> None:
        raise NotImplementedError


class CsvExporter(PortfolioExporter):
    def export(self, positions: Sequence[Position], path: str) -> None:
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["symbol", "kind", "quantity", "value"])
            for p in positions:
                writer.writerow([p.symbol, p.kind, str(p.quantity), str(p.value)])


class JsonExporter(PortfolioExporter):
    def export(self, positions: Sequence[Position], path: str) -> None:
        payload = [
            {
                "symbol": p.symbol,
                "kind": p.kind,
                "quantity": str(p.quantity),
                "value": str(p.value),
            }
            for p in positions
        ]
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)


# ---------------------------------------------------------------------------
# 4. PROOF OF OCP: a brand-new asset class, added without touching anything
#    above this line - not the repository, not the calculator, not the
#    exporters. This is the block to point at during your presentation.
# ---------------------------------------------------------------------------


@register_asset
@dataclass
class RealEstate(Asset):
    kind: ClassVar[str] = "real_estate"
    appraised_value: Decimal = Decimal("0")
    mortgage_balance: Decimal = Decimal("0")

    def market_value(self, prices: PriceProvider) -> Decimal:
        # Equity, not gross value - a valuation rule unique to this type.
        return (self.appraised_value - self.mortgage_balance) * self.quantity

    @property
    def details(self) -> Dict[str, str]:
        return {
            "appraised_value": str(self.appraised_value),
            "mortgage_balance": str(self.mortgage_balance),
        }


# ---------------------------------------------------------------------------
# 5. COMPOSITION ROOT - the only place that knows about concrete classes
# ---------------------------------------------------------------------------
# Everything is wired together here and injected downwards. Swapping the mock
# provider for the real one is a one-line change in this function.


def build_demo_portfolio() -> List[Asset]:
    return [
        Stock(symbol="AAPL", quantity=Decimal("12"), exchange="NASDAQ"),
        Stock(symbol="MSFT", quantity=Decimal("5"), exchange="NASDAQ"),
        Crypto(symbol="BTC", quantity=Decimal("0.35"), wallet="ledger"),
        Crypto(symbol="ETH", quantity=Decimal("4.2"), wallet="exchange"),
        CashSavings(symbol="EUR-SAVINGS", quantity=Decimal("7500"),
                    annual_rate=Decimal("0.0325")),
        RealEstate(symbol="FLAT-CHISINAU", quantity=Decimal("1"),
                   appraised_value=Decimal("85000"),
                   mortgage_balance=Decimal("41000")),
    ]


def demo_prices() -> PriceProvider:
    # DIP: `PortfolioCalculator` is given this object; for production, return
    # ApiPriceProvider(...) instead and change nothing else.
    return CachingPriceProvider(
        MockPriceProvider(
            {
                "AAPL": Decimal("214.50"),
                "MSFT": Decimal("432.10"),
                "BTC": Decimal("61250.00"),
                "ETH": Decimal("2980.75"),
            }
        )
    )


def main() -> None:
    repository = AssetRepository()            # SRP: storage
    calculator = PortfolioCalculator(demo_prices())  # SRP: maths (+ DIP)
    exporters: Dict[str, PortfolioExporter] = {      # SRP: reporting
        "portfolio.csv": CsvExporter(),
        "portfolio.json": JsonExporter(),
    }

    repository.add_many(build_demo_portfolio())
    assets = repository.list_all()

    positions = calculator.value_positions(assets)
    net_worth = calculator.net_worth(positions)
    allocation = calculator.allocation_by_kind(positions)

    print("PERSONAL WEALTH DASHBOARD")
    print("-" * 46)
    for position in positions:
        print("{:<16} {:<12} {:>14}".format(
            position.symbol, position.kind, "{:,}".format(position.value)))
    print("-" * 46)
    print("{:<29} {:>16}".format("NET WORTH", "{:,}".format(net_worth)))
    print()
    print("Allocation by asset class")
    for kind, percent in sorted(allocation.items(), key=lambda kv: -kv[1]):
        print("  {:<14} {:>6}%".format(kind, percent))

    for path, exporter in exporters.items():
        exporter.export(positions, path)
    print()
    print("Exported: " + ", ".join(exporters))

    repository.close()


if __name__ == "__main__":
    main()
