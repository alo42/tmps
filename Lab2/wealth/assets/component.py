"""
COMPOSITE - Component.

The single interface shared by an individual holding (a leaf) and a group of
holdings (a composite). Everything that values, stores or reports a portfolio
talks to this abstraction, so it never needs to know whether it was handed one
stock or an entire net-worth tree.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING, Iterator, Tuple

if TYPE_CHECKING:  # imported for type hints only - avoids an import cycle
    from wealth.assets.base import Asset
    from wealth.pricing.providers import PriceProvider

GroupPath = Tuple[str, ...]


class PortfolioComponent(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """Display name: a ticker for a holding, a label for a group."""

    @abstractmethod
    def market_value(self, prices: PriceProvider) -> Decimal:
        """Current value of this component (and of everything under it)."""

    @abstractmethod
    def walk(self, path: GroupPath = ()) -> Iterator[Tuple[GroupPath, Asset]]:
        """Yields every leaf holding together with the group names above it."""

    def holdings(self) -> Iterator[Asset]:
        """Every leaf holding, without the group path."""
        for _, asset in self.walk():
            yield asset

    def outline(self, depth: int = 0) -> Iterator[Tuple[int, PortfolioComponent]]:
        """Yields (depth, group) for every group in the tree. Leaves yield nothing."""
        return iter(())
