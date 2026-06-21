"""Governors — a vendored, dated snapshot (see data/governors.json).

Slow-changing, so we ship it rather than hit an API. Every record carries the
snapshot's ``as_of`` date so callers can judge freshness.
"""

from __future__ import annotations

import json
from importlib.resources import files

from whoreps_mcp.models import Official

_DATA: dict | None = None


def _load() -> dict:
    global _DATA
    if _DATA is None:
        _DATA = json.loads(
            (files("whoreps_mcp.data") / "governors.json").read_text(encoding="utf-8")
        )
    return _DATA


def governor_for(state: str) -> Official | None:
    data = _load()
    g = (data.get("governors") or {}).get(state)
    if not g:
        return None
    return Official(
        id=f"governor:{state}",
        name=g["name"],
        office="Governor",
        level="state",
        chamber="executive",
        district=None,
        party=g.get("party"),
        phone=g.get("phone"),
        website=g.get("website"),
        term_end=g.get("term_end"),
        source="vendored:governors.json",
        as_of=g.get("as_of") or data.get("as_of", ""),
    )
