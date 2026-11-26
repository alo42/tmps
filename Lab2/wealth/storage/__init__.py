"""Persistence: the shared database connection and the asset repository."""

from wealth.storage.database import Database
from wealth.storage.repository import AssetRepository

__all__ = ["AssetRepository", "Database"]
