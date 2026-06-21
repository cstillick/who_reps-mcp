"""Census Geocoder — address -> lat/lon, state, districts, and OCD divisions.

The Census geocoder is free and key-less. ``parse_geographies`` is pure (tested
against recorded fixtures); ``geocode`` adds the cached live fetch.

Divisions are derived OCD-IDs (the open identifiers Google's Divisions API
returned), built from the matched geographies.
"""

from __future__ import annotations

from typing import Any

import httpx

from whoreps_mcp.cache import Cache
from whoreps_mcp.config import Settings, get_settings
from whoreps_mcp.models import GeoResult

TERRITORY_LIKE = {"DC", "PR", "VI", "GU", "AS", "MP"}


class AddressNotFound(Exception):
    pass


def _first(geos: dict, contains: str) -> dict | None:
    for key, items in geos.items():
        if contains in key and items:
            return items[0]
    return None


def _cd_number(geos: dict) -> str | None:
    entry = _first(geos, "Congressional District")
    if not entry:
        return None
    if entry.get("BASENAME"):
        return entry["BASENAME"]
    for k, v in entry.items():
        if k.upper().startswith("CD") and v:
            return str(v)
    return None


def _sld_number(geos: dict, label: str) -> str | None:
    entry = _first(geos, label)
    return entry.get("BASENAME") if entry else None


def _build_divisions(state: str, cd: str | None, upper: str | None, lower: str | None) -> list[str]:
    if not state:
        return []
    divs = ["ocd-division/country:us"]
    if state == "DC":
        divs.append("ocd-division/country:us/district:dc")
        return divs
    base = f"ocd-division/country:us/state:{state.lower()}"
    divs.append(base)
    if cd:
        n = cd.lstrip("0") or "1"
        if n not in ("98", "99"):  # 98/99 are delegate/territory placeholders
            divs.append(f"{base}/cd:{n}")
    if upper:
        divs.append(f"{base}/sldu:{upper.lstrip('0') or upper}")
    if lower:
        divs.append(f"{base}/sldl:{lower.lstrip('0') or lower}")
    return divs


def parse_geographies(payload: dict[str, Any], address_in: str) -> GeoResult:
    """Pure: a Census geographies response -> GeoResult."""
    matches = (payload.get("result") or {}).get("addressMatches") or []
    if not matches:
        raise AddressNotFound(f"no Census match for {address_in!r}")
    m = matches[0]
    coords = m.get("coordinates") or {}
    geos = m.get("geographies") or {}

    state_entry = _first(geos, "States") or {}
    state = state_entry.get("STUSAB")
    state_fips = state_entry.get("STATE")
    cd = _cd_number(geos)
    upper = _sld_number(geos, "State Legislative Districts - Upper")
    lower = _sld_number(geos, "State Legislative Districts - Lower")

    state_leg = {}
    if upper:
        state_leg["upper"] = upper
    if lower:
        state_leg["lower"] = lower

    return GeoResult(
        matched_address=m.get("matchedAddress", address_in),
        lat=coords.get("y"),
        lon=coords.get("x"),
        state=state,
        state_fips=state_fips,
        congressional_district=cd,
        state_leg_districts=state_leg,
        divisions=_build_divisions(state, cd, upper, lower),
    )


def fetch_geographies(address: str, settings: Settings) -> dict:
    """Live (cached) fetch of the Census geographies payload for an address."""
    cache = Cache(settings)
    key = f"census:onelineaddress:{address.strip().lower()}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    resp = httpx.get(  # pragma: no cover - network
        f"{settings.census_base}/geographies/onelineaddress",
        params={
            "address": address,
            "benchmark": "Public_AR_Current",
            "vintage": "Current_Current",
            "layers": "all",
            "format": "json",
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    data = resp.json()
    cache.set(key, data)
    return data


def geocode(address: str, settings: Settings | None = None) -> GeoResult:
    settings = settings or get_settings()
    return parse_geographies(fetch_geographies(address, settings), address)
