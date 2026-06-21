# CLAUDE.md — whoreps-mcp

You are building an MCP server that takes a U.S. address and returns the elected officials for it. This file is your standing brief. Read `SPEC.md` for the full design and `BUILD_PLAN.md` for the ordered milestones. Work milestone by milestone; do not skip ahead.

## What this project is

A free, open MCP server that replaces the dead Google Civic Representatives API. Address → districts → officials, using only free public data.

## Core principles

- **Free inputs only.** Every data source must be free (free API key is fine, paid is not). If a source needs payment, find another or note it as out of scope.
- **Graceful degradation.** If state-legislator data is missing for a state, still return federal officials and say so. Never fail the whole request because one tier is unavailable.
- **Cache aggressively.** Districts for an address rarely change; member rosters change slowly. Cache geocoding and roster lookups locally (SQLite) with sensible TTLs.
- **Be honest about freshness.** Every response includes the data source and its as-of date. This is a civic tool; correctness and provenance matter more than cleverness.

## Tech stack (default)

- Python 3.11+, `uv` for env/deps.
- Official MCP SDK: `mcp` package, use `FastMCP` for ergonomic tool definitions.
- `httpx` for HTTP, `pydantic` for models, `sqlite3`/`sqlite-utils` for cache.
- Transport: stdio by default; expose a `--http` flag for Streamable HTTP later.
- (TypeScript alternative is acceptable if the user prefers — the SDK exists — but Python is the default because the data-joining work is simpler here.)

## Data sources (all free)

1. **Census Geocoder** — `https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress` returns lat/lon + geographies including the 119th Congressional District and (where available) state legislative districts. No API key.
2. **`unitedstates/congress-legislators`** — the canonical open YAML dataset of current federal legislators (GitHub, public domain). Use this for U.S. Senate + House rather than a live API; it's reliable and key-less. Mirror/cache it.
3. **Congress.gov API** (`api.congress.gov`, free key via api.data.gov) — optional enrichment for member detail/committees.
4. **OpenStates API v3** (`https://v3.openstates.org`, free key) — state legislators by district. This is the state-tier source.
5. **Governors** — small, slow-changing; seed from a maintained open list (e.g., a vendored JSON) and document the refresh process.

## Hard rules

- Do not scrape anything behind a login or a paywall.
- Do not hardcode secrets. Keys come from `.env` / environment.
- Every tool returns structured JSON *and* a short human-readable summary.
- Write tests against recorded fixtures (don't hit live APIs in CI).
- Keep a `CHANGELOG.md` and update it each milestone.

## Definition of done for v1

`lookup_officials("1600 Pennsylvania Ave NW, Washington, DC 20500")` returns the correct U.S. House delegate, both relevant federal tiers, and DC council where applicable, with sources and as-of dates, in under 2 seconds warm-cache. All four tools implemented, tested against fixtures, README usage accurate.
