"""Federal officials from the open `unitedstates/congress-legislators` dataset.

Key-less and reliable. ``officials_for`` is pure (state + CD -> 2 senators + the
House member/delegate); ``load_roster`` adds the cached live YAML fetch.
"""

from __future__ import annotations

import httpx
import yaml

from whoreps_mcp.cache import Cache
from whoreps_mcp.config import Settings, get_settings
from whoreps_mcp.models import Official
from whoreps_mcp.sources.census import TERRITORY_LIKE

SOURCE = "unitedstates/congress-legislators"
PHOTO = "https://theunitedstates.io/images/congress/225x275/{bioguide}.jpg"


def _current_term(legislator: dict) -> dict:
    terms = legislator.get("terms") or [{}]
    return terms[-1]  # current legislators: the active term is the last one


def _name(legislator: dict) -> str:
    n = legislator.get("name") or {}
    return n.get("official_full") or " ".join(p for p in [n.get("first"), n.get("last")] if p)


def _to_official(
    legislator: dict, term: dict, office: str, district: str | None, as_of: str
) -> Official:
    bioguide = (legislator.get("id") or {}).get("bioguide", "")
    state = term.get("state")
    if office == "U.S. Senator":
        oid = f"us_senate:{state}:{bioguide}"
        chamber = "upper"
    else:
        oid = f"us_house:{state}-{district or '0'}:{bioguide}"
        chamber = "lower"
    return Official(
        id=oid,
        name=_name(legislator),
        office=office,
        level="federal",
        chamber=chamber,
        district=district,
        party=term.get("party"),
        phone=term.get("phone"),
        website=term.get("url"),
        photo_url=PHOTO.format(bioguide=bioguide) if bioguide else None,
        term_end=term.get("end"),
        source=SOURCE,
        as_of=as_of,
    )


def officials_for(
    state: str, cd: str | None, legislators: list[dict], as_of: str
) -> list[Official]:
    """The federal slate for a state + congressional district."""
    out: list[Official] = []

    # Senators (none for DC / territories).
    for leg in legislators:
        term = _current_term(leg)
        if term.get("type") == "sen" and term.get("state") == state:
            out.append(_to_official(leg, term, "U.S. Senator", None, as_of))

    # House member / delegate.
    is_territory = state in TERRITORY_LIKE
    want = None if cd is None else (cd.lstrip("0") or "0")
    for leg in legislators:
        term = _current_term(leg)
        if term.get("type") != "rep" or term.get("state") != state:
            continue
        district = str(term.get("district", "0"))
        if is_territory:
            office = "U.S. Delegate"
            out.append(_to_official(leg, term, office, district, as_of))
            break
        if want is not None and district == want:
            out.append(_to_official(leg, term, "U.S. Representative", district, as_of))
            break

    return out


def find_by_bioguide(roster: list[dict], bioguide: str) -> dict | None:
    return next((leg for leg in roster if (leg.get("id") or {}).get("bioguide") == bioguide), None)


def official_from_id(official_id: str, roster: list[dict], as_of: str) -> Official | None:
    """Reconstruct a federal Official from a `us_senate:`/`us_house:` id."""
    parts = official_id.split(":")
    kind, bioguide = parts[0], parts[-1]
    leg = find_by_bioguide(roster, bioguide)
    if leg is None:
        return None
    term = _current_term(leg)
    if kind == "us_senate":
        return _to_official(leg, term, "U.S. Senator", None, as_of)
    district = (
        parts[1].split("-")[-1]
        if len(parts) > 1 and "-" in parts[1]
        else str(term.get("district", "0"))
    )
    office = "U.S. Delegate" if term.get("state") in TERRITORY_LIKE else "U.S. Representative"
    return _to_official(leg, term, office, district, as_of)


def committees_for(bioguide: str, settings: Settings) -> list[dict]:  # pragma: no cover - network
    """Committee memberships via Congress.gov (enrichment). [] without a key."""
    if not settings.congress_gov_api_key:
        return []
    resp = httpx.get(
        f"{settings.congress_gov_base}/member/{bioguide}",
        params={"api_key": settings.congress_gov_api_key, "format": "json"},
        timeout=30.0,
    )
    resp.raise_for_status()
    member = (resp.json() or {}).get("member") or {}
    return member.get("committeeAssignments") or member.get("committees") or []


def load_roster(settings: Settings | None = None) -> list[dict]:
    """Live (cached) load of legislators-current.yaml."""
    settings = settings or get_settings()
    cache = Cache(settings)
    cached = cache.get("federal:roster")
    if cached is not None:
        return cached
    resp = httpx.get(settings.legislators_url, timeout=60.0)  # pragma: no cover - network
    resp.raise_for_status()
    legislators = yaml.safe_load(resp.text)
    cache.set("federal:roster", legislators)
    return legislators
