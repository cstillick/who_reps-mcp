"""M1: geocoding parses Census geographies into districts + OCD divisions."""

from __future__ import annotations

import json
from pathlib import Path

from whoreps_mcp.cache import Cache
from whoreps_mcp.config import get_settings
from whoreps_mcp.sources.census import geocode, parse_geographies

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_parse_ok5_districts_and_divisions() -> None:
    geo = parse_geographies(
        _load("census_ok5.json"), "2300 N Lincoln Blvd, Oklahoma City, OK 73105"
    )
    assert geo.state == "OK"
    assert geo.state_fips == "40"
    assert geo.congressional_district == "5"
    assert geo.lat == 35.4923 and geo.lon == -97.5037
    assert geo.state_leg_districts == {"upper": "48", "lower": "88"}
    assert geo.divisions == [
        "ocd-division/country:us",
        "ocd-division/country:us/state:ok",
        "ocd-division/country:us/state:ok/cd:5",
        "ocd-division/country:us/state:ok/sldu:48",
        "ocd-division/country:us/state:ok/sldl:88",
    ]


def test_parse_dc_degrades_without_state_legislature() -> None:
    geo = parse_geographies(
        _load("census_dc.json"), "1600 Pennsylvania Ave NW, Washington, DC 20500"
    )
    assert geo.state == "DC"
    assert geo.congressional_district == "98"  # delegate district
    assert geo.state_leg_districts == {}  # DC has no state legislature
    assert geo.divisions == ["ocd-division/country:us", "ocd-division/country:us/district:dc"]


def test_geocode_uses_cache_offline() -> None:
    # Pre-seed the cache so geocode() returns without any network call.
    settings = get_settings()
    address = "2300 N Lincoln Blvd, Oklahoma City, OK 73105"
    Cache(settings).set(f"census:onelineaddress:{address.lower()}", _load("census_ok5.json"))
    geo = geocode(address, settings)
    assert geo.state == "OK"
    assert geo.congressional_district == "5"
