"""OpenStates v3 — state legislators by point (the cleanest path: lat/lng in,
legislators out, no manual district math).

``parse_people`` is pure (tested against a recorded fixture); ``people_geo`` adds
the cached live fetch and degrades to ``[]`` when no API key is configured.
"""

from __future__ import annotations

import httpx

from whoreps_mcp.cache import Cache
from whoreps_mcp.config import Settings
from whoreps_mcp.models import Official

SOURCE = "openstates"


def parse_people(payload: dict, as_of: str) -> list[Official]:
    out: list[Official] = []
    for p in payload.get("results", []):
        role = p.get("current_role") or {}
        oc = role.get("org_classification")
        if oc == "upper":
            office = "State Senator"
        elif oc == "lower":
            office = "State Representative"
        else:
            office = role.get("title") or "State Legislator"

        phone = None
        for office_rec in p.get("offices") or []:
            if office_rec.get("voice"):
                phone = office_rec["voice"]
                break

        district = role.get("district")
        out.append(
            Official(
                id=p.get("id"),
                name=p.get("name"),
                office=office,
                level="state",
                chamber=oc if oc in ("upper", "lower") else None,
                district=str(district) if district is not None else None,
                party=p.get("party"),
                phone=phone,
                website=p.get("openstates_url"),
                photo_url=p.get("image") or None,
                term_end=role.get("end_date"),
                source=SOURCE,
                as_of=as_of,
            )
        )
    return out


def fetch_people_geo(
    lat: float, lng: float, settings: Settings
) -> dict:  # pragma: no cover - network
    cache = Cache(settings)
    key = f"openstates:geo:{round(lat, 4)}:{round(lng, 4)}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    resp = httpx.get(
        f"{settings.openstates_base}/people.geo",
        params={"lat": lat, "lng": lng},
        headers={"X-API-Key": settings.openstates_api_key or ""},
        timeout=30.0,
    )
    resp.raise_for_status()
    data = resp.json()
    cache.set(key, data)
    return data


def people_geo(lat: float, lng: float, settings: Settings, as_of: str) -> list[Official]:
    """State legislators for a point. Returns [] (degrade) when no key is set."""
    if not settings.openstates_api_key:
        return []
    return parse_people(fetch_people_geo(lat, lng, settings), as_of)
