"""
FACTORY METHOD - parameterised variant (GoF, "Implementation" note 2).

`AssetFactory.create(kind, ...)` instantiates the right `Asset` subclass from a
type tag read out of storage. Concrete classes register themselves with
`@AssetFactory.register`, so the factory - and the repository that calls it -
never names Stock, Crypto, CashSavings or RealEstate.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Type

from wealth.assets.base import Asset


class AssetFactory:
    _registry: Dict[str, Type[Asset]] = {}

    @classmethod
    def register(cls, asset_cls: Type[Asset]) -> Type[Asset]:
        """Class decorator: makes `asset_cls` creatable by its `kind` tag."""
        cls._registry[asset_cls.kind] = asset_cls
        return asset_cls

    @classmethod
    def create(cls, kind: str, symbol: str, quantity: object,
               details: Optional[Dict[str, str]] = None) -> Asset:
        asset_cls = cls._registry.get(kind)
        if asset_cls is None:
            raise ValueError("Unknown asset kind %r (known: %s)"
                             % (kind, ", ".join(cls.kinds())))
        return asset_cls.from_details(symbol, str(quantity), details or {})

    @classmethod
    def kinds(cls) -> List[str]:
        return sorted(cls._registry)
