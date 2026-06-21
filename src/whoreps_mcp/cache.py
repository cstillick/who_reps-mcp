"""A tiny SQLite key/value cache with TTL.

Districts for an address rarely change and member rosters change slowly, so we
cache geocodes and roster fetches locally and serve them for ``cache_ttl_seconds``.
"""

from __future__ import annotations

import json
import sqlite3
import time
from typing import Any

from whoreps_mcp.config import Settings, get_settings


class Cache:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.settings.ensure_dirs()
        self.path = str(self.settings.cache_path)
        self.ttl = self.settings.cache_ttl_seconds
        with self._con() as con:
            con.execute(
                "CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT, ts REAL)"
            )

    def _con(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def get(self, key: str) -> Any | None:
        with self._con() as con:
            row = con.execute("SELECT value, ts FROM cache WHERE key = ?", (key,)).fetchone()
        if not row:
            return None
        value, ts = row
        if self.ttl and (time.time() - ts) > self.ttl:
            return None
        return json.loads(value)

    def set(self, key: str, value: Any) -> None:
        with self._con() as con:
            con.execute(
                "INSERT OR REPLACE INTO cache (key, value, ts) VALUES (?, ?, ?)",
                (key, json.dumps(value), time.time()),
            )
