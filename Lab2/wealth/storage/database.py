"""
SINGLETON - one SQLite connection per process.

Every repository shares the same connection, so they all see the same data
and the application never opens the database file twice. Creation is guarded
by a lock (double-checked locking) so two threads cannot race to create it.
"""

from __future__ import annotations

import sqlite3
import threading
from typing import Optional


class Database:
    _instance: Optional[Database] = None
    _lock = threading.Lock()

    _path: str
    _connection: sqlite3.Connection

    def __new__(cls, path: Optional[str] = None) -> Database:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # re-check inside the lock
                    instance = super().__new__(cls)
                    instance._path = path or ":memory:"
                    instance._connection = sqlite3.connect(
                        instance._path, check_same_thread=False)
                    cls._instance = instance
        elif path is not None and path != cls._instance._path:
            # Silently returning the old connection would hide a real bug.
            raise RuntimeError("Database already open at %r; cannot reopen it at %r"
                               % (cls._instance._path, path))
        return cls._instance

    @classmethod
    def instance(cls) -> Database:
        """The shared instance, created on first use."""
        return cls()

    @property
    def path(self) -> str:
        return self._path

    @property
    def connection(self) -> sqlite3.Connection:
        return self._connection

    @classmethod
    def _reset(cls) -> None:
        """Test hook: closes and forgets the instance. Not for application code."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance._connection.close()
            cls._instance = None
