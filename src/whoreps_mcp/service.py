"""Orchestration: address -> geocode -> rosters -> a merged OfficialsResponse.

Sources can be injected (``legislators=...``) so the whole flow is testable
offline against fixtures; by default they're fetched live (cached). The state
tier (OpenStates + governors) is added in M4.
"""

from __future__ import annotations

from datetime import date

from whoreps_mcp.config import Settings, get_settings
from whoreps_mcp.models import OfficialsResponse
from whoreps_mcp.sources import census, federal
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
    as_of: str | None = None,
) -> OfficialsResponse:
    settings = settings or get_settings()
    as_of = as_of or date.today().isoformat()

    geo = census.geocode(address, settings)
    roster = legislators if legislators is not None else federal.load_roster(settings)
    officials = federal.officials_for(geo.state, geo.congressional_district, roster, as_of)

    notes: list[str] = []
    if geo.state in TERRITORY_LIKE:
        notes.append(
            f"{geo.state} has no U.S. Senators; its U.S. House seat is a non-voting delegate."
        )
    if not geo.state_leg_districts:
        notes.append(
            "No state legislative districts for this address (e.g. DC has no state legislature)."
        )

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
