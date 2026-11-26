"""
FACADE - one simple entry point over the whole subsystem.

A client (the CLI, a future web UI, the unit tests) needs four things: save a
portfolio, get a summary, print it, export it. Behind those four calls sit a
singleton database, a repository, a factory-method price source, a calculator,
a decorator-based liquidation policy and a family of exporters - none of which
the client has to know about.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Type

from wealth.assets.component import PortfolioComponent
from wealth.pricing.sources import DemoMarketData, MarketDataSource
from wealth.reporting.console import render_summary
from wealth.reporting.exporters import CsvExporter, JsonExporter, PortfolioExporter
from wealth.storage.database import Database
from wealth.storage.repository import AssetRepository
from wealth.valuation.calculator import PortfolioCalculator, Position
from wealth.valuation.fees import LiquidationPolicy


@dataclass(frozen=True)
class DashboardSummary:
    portfolio_name: str
    data_source: str
    positions: List[Position]
    breakdown: List[Tuple[int, str, Decimal]]
    net_worth: Decimal
    liquidation_value: Decimal
    allocation: Dict[str, Decimal]

    @property
    def selling_cost(self) -> Decimal:
        return self.net_worth - self.liquidation_value


class WealthDashboard:

    _EXPORTERS: Dict[str, Type[PortfolioExporter]] = {
        exporter.extension: exporter for exporter in (CsvExporter, JsonExporter)
    }

    def __init__(self, market: Optional[MarketDataSource] = None,
                 policy: Optional[LiquidationPolicy] = None,
                 database: Optional[Database] = None):
        self._market = market or DemoMarketData()
        self._policy = policy or LiquidationPolicy.default()
        self._repository = AssetRepository(database or Database.instance())
        self._calculator = PortfolioCalculator(self._market.provider())

    # --- the whole public surface ------------------------------------------

    def save_portfolio(self, portfolio: PortfolioComponent) -> int:
        """Stores a portfolio (replacing the previous one). Returns holdings saved."""
        return self._repository.save(portfolio)

    def summary(self) -> DashboardSummary:
        portfolio = self._repository.load()
        positions = self._calculator.value_positions(portfolio, self._policy)
        return DashboardSummary(
            portfolio_name=portfolio.name,
            data_source=self._market.description,
            positions=positions,
            breakdown=self._calculator.breakdown(portfolio),
            net_worth=self._calculator.net_worth(positions),
            liquidation_value=self._calculator.liquidation_value(positions),
            allocation=self._calculator.allocation_by_kind(positions),
        )

    def report(self) -> str:
        """The summary as printable text."""
        return render_summary(self.summary())

    def export(self, path: str) -> str:
        """Exports positions; the format is chosen from the file extension."""
        extension = os.path.splitext(path)[1].lower()
        exporter_cls = self._EXPORTERS.get(extension)
        if exporter_cls is None:
            raise ValueError("Unsupported export format %r (supported: %s)"
                             % (extension, ", ".join(sorted(self._EXPORTERS))))
        exporter_cls().export(self.summary().positions, path)
        return path
