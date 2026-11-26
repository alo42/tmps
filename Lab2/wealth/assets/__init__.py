"""Holdings, groups, and the creational patterns that produce them."""

# Importing the concrete types registers them with AssetFactory.
from wealth.assets.base import Asset
from wealth.assets.builder import BuilderError, PortfolioBuilder, PortfolioDirector
from wealth.assets.cash import CashSavings
from wealth.assets.component import PortfolioComponent
from wealth.assets.crypto import Crypto
from wealth.assets.factory import AssetFactory
from wealth.assets.group import AssetGroup
from wealth.assets.real_estate import RealEstate
from wealth.assets.stock import Stock

__all__ = [
    "Asset", "AssetFactory", "AssetGroup", "BuilderError", "CashSavings", "Crypto",
    "PortfolioBuilder", "PortfolioComponent", "PortfolioDirector", "RealEstate", "Stock",
]
