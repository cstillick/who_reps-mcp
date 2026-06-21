"""Shared fixtures. Isolate the cache to a temp path so tests never touch the repo."""

from __future__ import annotations

import os
import tempfile

import pytest


@pytest.fixture(scope="session", autouse=True)
def _isolated_cache() -> None:
    d = tempfile.mkdtemp(prefix="whoreps-test-")
    os.environ["CACHE_PATH"] = os.path.join(d, "cache.sqlite")
    yield
