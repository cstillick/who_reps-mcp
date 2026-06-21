# BUILD_PLAN — whoreps-mcp

Ordered milestones for Claude Code. Each milestone ends in a working, committed state. Don't move on until the "Done when" check passes.

## Handoff prompt (paste into Claude Code at repo root)

> Read CLAUDE.md and SPEC.md. Build this MCP server milestone by milestone per BUILD_PLAN.md, committing after each milestone. Use Python 3.11+, uv, and the official `mcp` SDK (FastMCP). Stub external calls behind a `sources/` package so they can be tested against fixtures. Ask me only if a data source is unavailable or requires payment; otherwise proceed.

---

### M0 — Scaffold
- `pyproject.toml` (uv), package `whoreps_mcp/`, entry point `whoreps-mcp`.
- `FastMCP` server that starts over stdio and exposes a `ping` tool.
- `.env.example` with `OPENSTATES_API_KEY`, `CONGRESS_GOV_API_KEY` (optional), `CACHE_PATH`.
- `.gitignore`, `LICENSE` (MIT), `CHANGELOG.md`.
- **Done when:** `uv run whoreps-mcp` starts and an MCP client lists the `ping` tool.

### M1 — Geocoding
- `sources/census.py`: address → `{lat, lon, state, congressional_district, state_leg_districts[], divisions[]}`.
- Build OCD-IDs from the geographies.
- SQLite cache with TTL.
- **Done when:** a unit test geocodes a known address to the correct CD and divisions from a recorded fixture.

### M2 — Federal officials
- `sources/federal.py`: load/cache `legislators-current.yaml`; map state + CD → 2 senators + 1 representative.
- Normalize to `Official`.
- **Done when:** given a state+CD, returns the correct three federal officials with party, website, term_end, source, as_of.

### M3 — `lookup_officials` (federal tier) end to end
- Wire geocode → federal roster → `OfficialsResponse`.
- Implement `list_districts` too.
- **Done when:** `lookup_officials("<known address>")` returns correct federal slate + divisions, with text summary, against fixtures.

### M4 — State tier
- `sources/openstates.py`: prefer `people.geo` (lat/lng → state legislators); fall back to district matching.
- `sources/governors.py`: vendored JSON + documented refresh.
- Merge into the response; add `coverage_notes` when a tier is missing.
- **Done when:** response includes governor + state legislators for a covered state, and degrades cleanly for a gap.

### M5 — Detail + enrichment
- `get_official_details`: committees/contact via Congress.gov (federal) and OpenStates (state).
- `lookup_by_district`.
- **Done when:** all four tools implemented and returning structured + text output.

### M6 — Hardening
- Recorded-fixture test suite; CI (GitHub Actions) green with no live calls.
- Error handling for bad addresses, territories, PO boxes.
- README usage verified; CHANGELOG updated; tag `v0.1.0`.
- **Done when:** `pytest` passes offline and the README quick-start works on a clean checkout.

### M7 (optional) — Distribution
- `--http` Streamable HTTP transport.
- Publish to PyPI and submit to an MCP registry (PulseMCP/Glama) for discoverability.

## Test addresses (sanity set)
- `1600 Pennsylvania Ave NW, Washington, DC 20500` (DC, no state legislature — exercises degradation)
- A known OK-5 address (your turf; exercises state tier)
- A rural multi-county address (district edge cases)
- A territory address (graceful failure path)
