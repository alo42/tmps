"""
COMPOSITE - Composite.

A named group of components - accounts, sub-portfolios, the whole net worth.
Its value is the sum of its children, and because children are themselves
`PortfolioComponent`s, groups nest to any depth.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Iterable, Iterator, List, Tuple

from wealth.assets.component import GroupPath, PortfolioComponent
from wealth.money import ZERO

if TYPE_CHECKING:
    from wealth.assets.base import Asset
    from wealth.pricing.providers import PriceProvider


class AssetGroup(PortfolioComponent):

    def __init__(self, name: str, children: Iterable[PortfolioComponent] = ()):
        self._name = name
        self._children: List[PortfolioComponent] = list(children)

    @property
    def name(self) -> str:
        return self._name

    @property
    def children(self) -> Tuple[PortfolioComponent, ...]:
        return tuple(self._children)

    def add(self, component: PortfolioComponent) -> AssetGroup:
        self._children.append(component)
        return self

    def remove(self, component: PortfolioComponent) -> None:
        self._children.remove(component)

    def subgroup(self, name: str) -> AssetGroup:
        """Returns the child group called `name`, creating it if needed."""
        for child in self._children:
            if isinstance(child, AssetGroup) and child.name == name:
                return child
        group = AssetGroup(name)
        self.add(group)
        return group

    # --- the uniform interface: identical calls for one asset or a whole tree

    def market_value(self, prices: PriceProvider) -> Decimal:
        return sum((child.market_value(prices) for child in self._children), ZERO)

    def walk(self, path: GroupPath = ()) -> Iterator[Tuple[GroupPath, Asset]]:
        here = path + (self._name,)
        for child in self._children:
            yield from child.walk(here)

    def outline(self, depth: int = 0) -> Iterator[Tuple[int, PortfolioComponent]]:
        yield depth, self
        for child in self._children:
            yield from child.outline(depth + 1)

    def __repr__(self) -> str:
        return "AssetGroup(%r, %d children)" % (self._name, len(self._children))
