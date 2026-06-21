# SPEC — whoreps-mcp

## Problem

Google's Civic Information Representatives API was turned down April 30, 2025. It was the standard "address → elected officials" primitive. Replacements are paid (BallotReady, Cicero, Ballotpedia). No clean, free MCP exists for this. We build one from open data.

## Users

Civic-app developers, advocacy/GOTV tools, journalists, anyone who needs "who represents this address" inside an agent or app.

## Scope (v1)

- Input: a U.S. street address (one-line or components) OR a lat/lon.
- Output: federal officials (2 U.S. Senators, 1 U.S. House member) + state tier (Governor, state upper- and lower-chamber legislators).
- Coverage: all 50 states + DC for the federal tier; state-legislator tier wherever OpenStates has district data (most states).
- Out of scope for v1: local/municipal officials, candidates (vs. officeholders), historical lookups, ballot/polling-place info. Note these as v2 in the roadmap.

## Architecture

```
address ──▶ Geocoder (Census) ──▶ {lat/lon, congressional district, state leg districts, state, FIPS}
                                        │
                 ┌──────────────────────┼───────────────────────┐
                 ▼                      ▼                         ▼
        Federal roster          State legislators          Governor lookup
   (congress-legislators YAML)   (OpenStates API v3)      (vendored JSON)
                 └──────────────────────┼───────────────────────┘
                                        ▼
                            Merge + normalize to Official[]
                                        ▼
                          Cache (SQLite) + structured response
```

## Data model

```python
class Official(BaseModel):
    id: str                 # stable id, e.g. "us_house:OK-5" or openstates ocd id
    name: str
    office: str             # "U.S. Senator", "State Representative", ...
    level: Literal["federal", "state"]
    chamber: str | None     # "upper" | "lower" | "executive"
    district: str | None
    party: str | None
    phone: str | None
    website: str | None
    photo_url: str | None
    term_end: str | None
    source: str             # which dataset
    as_of: str              # ISO date the source data was current

class OfficialsResponse(BaseModel):
    matched_address: str
    divisions: list[str]    # OCD-IDs for the address
    officials: list[Official]
    coverage_notes: list[str]   # e.g. "state legislators unavailable for territory X"
```

## MCP tools

| Tool | Args | Returns |
|---|---|---|
| `lookup_officials` | `address: str` (or `lat`,`lon`) | `OfficialsResponse` |
| `lookup_by_district` | `state, chamber, district` | `Official[]` |
| `get_official_details` | `official_id` | enriched `Official` (committees, full contact) |
| `list_districts` | `address` | `{matched_address, divisions[]}` |

Each tool returns JSON in `structuredContent` plus a concise text summary.

## Endpoints / references

- Census geocoder geographies: `https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?address=...&benchmark=Public_AR_Current&vintage=Current_Current&layers=all&format=json`
- congress-legislators: `https://github.com/unitedstates/congress-legislators` (`legislators-current.yaml`)
- OpenStates v3: `https://v3.openstates.org/people.geo?lat=..&lng=..` (geo lookup by point) and `https://v3.openstates.org/people?jurisdiction=..&org_classification=..`
- Congress.gov: `https://api.congress.gov/v3/member?...` (enrichment only)

## Non-functional

- Warm-cache `lookup_officials` < 2s; cold < 6s.
- No secrets in code; keys via env.
- CI runs against recorded fixtures (use `respx`/`vcr`-style recordings), never live.
- MIT license.

## Risks / notes

- Census state-legislative-district layers vary in vintage; verify the `layers`/`vintage` combination per state and document gaps.
- OpenStates `people.geo` is the cleanest path (point → legislators) and avoids manual district math — prefer it; fall back to district-number matching if geo is unavailable.
- Address edge cases (PO boxes, new construction, territories) must degrade gracefully with `coverage_notes`.
