"""Orchestration: address -> geocode -> rosters -> a merged OfficialsResponse.

Sources can be injected (``legislators=...``) so the whole flow is testable
offline against fixtures; by default they're fetched live (cached). The state
tier (OpenStates + governors) is added in M4.
"""

from __future__ import annotations

from datetime import date

from whoreps_mcp.config import Settings, get_settings
from whoreps_mcp.models import OfficialsResponse
from whoreps_mcp.sources import census, federal, governors, openstates
from whoreps_mcp.sources.census import TERRITORY_LIKE

_PARTY_ABBR = {
    "Republican": "R",
    "Democrat": "D",
    "Democratic": "D",
    "Independent": "I",
    "Libertarian": "L",
}


def lookup_officials(
    address: str,
    *,
    settings: Settings | None = None,
    legislators: list[dict] | None = None,
    openstates_payload: dict | None = None,
    as_of: str | None = None,
) -> OfficialsResponse:
    settings = settings or get_settings()
    as_of = as_of or date.today().isoformat()

    geo = census.geocode(address, settings)
    notes: list[str] = []

    # Federal tier.
    roster = legislators if legislators is not None else federal.load_roster(settings)
    officials = federal.officials_for(geo.state, geo.congressional_district, roster, as_of)
    if geo.state in TERRITORY_LIKE:
        notes.append(
            f"{geo.state} has no U.S. Senators; its U.S. House seat is a non-voting delegate."
        )

    # State executive tier (Governor).
    governor = governors.governor_for(geo.state)
    if governor is not None:
        officials.append(governor)
    elif geo.state == "DC":
        notes.append("DC has a Mayor, not a Governor; not included.")
    else:
        notes.append(f"Governor data unavailable for {geo.state}.")

    # State legislative tier (OpenStates).
    if not geo.state_leg_districts:
        notes.append(
            "No state legislative districts for this address (e.g. DC has no state legislature)."
        )
    elif openstates_payload is not None:
        officials += openstates.parse_people(openstates_payload, as_of)
    elif settings.openstates_api_key and geo.lat and geo.lon:
        officials += openstates.people_geo(geo.lat, geo.lon, settings, as_of)
    else:
        notes.append("State legislators omitted — set OPENSTATES_API_KEY to include them.")

    return OfficialsResponse(
        matched_address=geo.matched_address,
        divisions=geo.divisions,
        officials=officials,
        coverage_notes=notes,
    )


def list_districts(address: str, *, settings: Settings | None = None) -> dict:
    geo = census.geocode(address, settings or get_settings())
    return {
        "matched_address": geo.matched_address,
        "state": geo.state,
        "congressional_district": geo.congressional_district,
        "state_leg_districts": geo.state_leg_districts,
        "divisions": geo.divisions,
    }


def lookup_by_district(
    state: str,
    chamber: str,
    district: str | None = None,
    *,
    settings: Settings | None = None,
    legislators: list[dict] | None = None,
    as_of: str | None = None,
) -> list:
    """Officials for a chamber + district, skipping geocoding.

    ``chamber``: senate | house (federal), or upper | lower (state).
    """
    settings = settings or get_settings()
    as_of = as_of or date.today().isoformat()
    state = state.upper()
    ch = chamber.lower()

    if ch in ("senate", "us_senate", "sen"):
        roster = legislators if legislators is not None else federal.load_roster(settings)
        return [
            o
            for o in federal.officials_for(state, None, roster, as_of)
            if o.office == "U.S. Senator"
        ]

    if ch in ("house", "us_house", "rep", "representative", "cd"):
        roster = legislators if legislators is not None else federal.load_roster(settings)
        return [
            o
            for o in federal.officials_for(state, district, roster, as_of)
            if o.office in ("U.S. Representative", "U.S. Delegate")
        ]

    if ch in ("upper", "lower", "state_senate", "state_house"):
        oc = "upper" if ch in ("upper", "state_senate") else "lower"
        return openstates.people_by_district(state, oc, district, settings, as_of)

    raise ValueError(f"unknown chamber {chamber!r}; use senate|house|upper|lower")


def get_official_details(
    official_id: str,
    *,
    settings: Settings | None = None,
    legislators: list[dict] | None = None,
    as_of: str | None = None,
) -> dict:
    """Enriched detail for one official (committees/contact where available)."""
    settings = settings or get_settings()
    as_of = as_of or date.today().isoformat()

    if official_id.startswith("governor:"):
        gov = governors.governor_for(official_id.split(":", 1)[1])
        if gov is None:
            return {"id": official_id, "found": False}
        return {**gov.model_dump(), "committees": []}

    if official_id.startswith(("us_senate:", "us_house:")):
        roster = legislators if legislators is not None else federal.load_roster(settings)
        official = federal.official_from_id(official_id, roster, as_of)
        if official is None:
            return {"id": official_id, "found": False}
        bioguide = official_id.split(":")[-1]
        return {**official.model_dump(), "committees": federal.committees_for(bioguide, settings)}

    if official_id.startswith("ocd-person/"):
        if not settings.openstates_api_key:
            return {
                "id": official_id,
                "found": False,
                "note": "Set OPENSTATES_API_KEY to fetch state-official detail.",
            }
        detail = openstates.person_detail(
            official_id, settings, as_of
        )  # pragma: no cover - network
        return detail

    return {"id": official_id, "found": False, "note": "unrecognized id"}


def summarize(resp: OfficialsResponse) -> str:
    """A concise human-readable one-liner to accompany the structured output."""
    if not resp.officials:
        return f"No officials found for {resp.matched_address}."
    parts = []
    for o in resp.officials:
        bits = []
        if o.party:
            bits.append(_PARTY_ABBR.get(o.party, o.party))
        if o.district:
            bits.append(o.district)
        tag = f" ({', '.join(bits)})" if bits else ""
        parts.append(f"{o.office} {o.name}{tag}")
    text = f"{len(resp.officials)} officials for {resp.matched_address}: " + "; ".join(parts) + "."
    if resp.coverage_notes:
        text += " " + " ".join(resp.coverage_notes)
    return text
