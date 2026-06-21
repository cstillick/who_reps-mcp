"""M6: bad addresses degrade gracefully instead of raising."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from whoreps_mcp import service
from whoreps_mcp.cache import Cache
from whoreps_mcp.config import get_settings
from whoreps_mcp.sources.census import AddressNotFound, parse_geographies

FIXTURES = Path(__file__).parent / "fixtures"
BAD = "123 Nowhere Pretend St, Atlantis, ZZ 00000"


def test_parse_no_match_raises() -> None:
    with pytest.raises(AddressNotFound):
        parse_geographies(json.loads((FIXTURES / "census_nomatch.json").read_text()), BAD)


@pytest.fixture(autouse=True)
def _seed_nomatch():
    Cache(get_settings()).set(
        f"census:onelineaddress:{BAD.lower()}",
        json.loads((FIXTURES / "census_nomatch.json").read_text()),
    )


def test_lookup_officials_degrades_on_bad_address() -> None:
    resp = service.lookup_officials(BAD)
    assert resp.officials == []
    assert resp.matched_address == BAD
    assert any("No geocode match" in n for n in resp.coverage_notes)


def test_list_districts_degrades_on_bad_address() -> None:
    out = service.list_districts(BAD)
    assert out["found"] is False
