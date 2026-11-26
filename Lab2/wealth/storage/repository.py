"""
Persistence (SRP from Lab 1): stores a portfolio tree and rebuilds it.

The connection comes from the `Database` singleton, injected so tests can
substitute it; asset objects are recreated through `AssetFactory`.
"""

from __future__ import annotations

import json
from typing import Optional

from wealth.assets.component import PortfolioComponent
from wealth.assets.factory import AssetFactory
from wealth.assets.group import AssetGroup
from wealth.storage.database import Database


class AssetRepository:

    def __init__(self, database: Optional[Database] = None):
        self._db = database or Database.instance()
        self._create_schema()

    def _create_schema(self) -> None:
        conn = self._db.connection
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS assets (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                group_path TEXT NOT NULL,  -- e.g. 'Investments/Stocks'
                kind       TEXT NOT NULL,
                symbol     TEXT NOT NULL,
                quantity   TEXT NOT NULL,  -- Decimal stored as text
                details    TEXT NOT NULL   -- type-specific fields as JSON
            )
            """
        )
        conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
        conn.commit()

    def save(self, portfolio: PortfolioComponent) -> int:
        """Replaces the stored portfolio. Returns the number of holdings saved."""
        conn = self._db.connection
        with conn:  # one transaction: all rows or none
            conn.execute("DELETE FROM assets")
            conn.execute("INSERT OR REPLACE INTO meta VALUES ('root_name', ?)",
                         (portfolio.name,))
            count = 0
            for path, asset in portfolio.walk():
                conn.execute(
                    "INSERT INTO assets (group_path, kind, symbol, quantity, details)"
                    " VALUES (?, ?, ?, ?, ?)",
                    ("/".join(path[1:]), asset.kind, asset.symbol,
                     str(asset.quantity), json.dumps(asset.details)),
                )
                count += 1
        return count

    def load(self) -> AssetGroup:
        """Rebuilds the tree; group nodes are recreated from the stored paths."""
        conn = self._db.connection
        row = conn.execute("SELECT value FROM meta WHERE key = 'root_name'").fetchone()
        root = AssetGroup(row[0] if row else "Net worth")
        rows = conn.execute(
            "SELECT group_path, kind, symbol, quantity, details FROM assets ORDER BY id")
        for group_path, kind, symbol, quantity, details in rows:
            node = root
            for part in filter(None, group_path.split("/")):
                node = node.subgroup(part)
            node.add(AssetFactory.create(kind, symbol, quantity, json.loads(details)))
        return root
