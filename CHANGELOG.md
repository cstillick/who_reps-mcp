# Changelog

All notable changes to this project will be documented here.

## [Unreleased]

### M5 — Detail + enrichment
- `get_official_details(official_id)`: reconstructs a federal official from the roster (committees via Congress.gov when keyed), a governor from the vendored data, or a state official via OpenStates; degrades cleanly without keys.
- `lookup_by_district(state, chamber, district)`: federal (senate/house) from the roster; state (upper/lower) via OpenStates. All four MCP tools + matching CLI commands now implemented and tested, incl. a fully offline MCP lookup flow.

### M4 — State tier
- `sources/openstates.py`: `people.geo` (lat/lng → state legislators), pure `parse_people` + cached live `people_geo` that degrades to `[]` without a key.
- `sources/governors.py` + `data/governors.json`: vendored, dated governor snapshot (all 50 states) with `as_of` surfaced on every record; refresh process in `docs/governors.md`.
- Service merges governor + state legislators and emits `coverage_notes` for gaps (DC: no senators, Mayor not Governor, no state legislature). Federal tier always returns even when state tiers are missing.

### M3 — `lookup_officials` (federal tier) end to end
- `service.py`: geocode → federal roster → `OfficialsResponse`, with coverage notes (no senators for DC/territories, missing state legislature) and a concise text summary. Sources injectable for offline tests.
- MCP tools `lookup_officials` + `list_districts`; CLI `lookup` / `districts`.

### M2 — Federal officials
- `sources/federal.py`: `unitedstates/congress-legislators` roster → state + CD → 2 U.S. Senators + the House member (or delegate for DC/territories), normalized to `Official` with party, website, phone, term_end, photo, source, as_of. Pure `officials_for` + cached live `load_roster`.
- Vendored YAML fixture (real current OK + DC officials) drives offline tests.

### M1 — Geocoding (Census)
- `sources/census.py`: address → `GeoResult` (lat/lon, state, congressional district, state-leg districts, derived OCD divisions). Pure `parse_geographies` + cached live `geocode`.
- `cache.py`: SQLite key/value cache with TTL.
- Tests against recorded Census fixtures (OK-5 + DC degradation path).

### M0 — Scaffold
- `pyproject.toml` (uv, hatchling, src layout); package `whoreps_mcp` with `sources/` subpackage.
- Typed `Settings` (optional `OPENSTATES_API_KEY` / `CONGRESS_GOV_API_KEY`, `CACHE_PATH`); pydantic models (`GeoResult`, `Official`, `OfficialsResponse`).
- FastMCP server with `ping`; `whoreps-mcp` entry point (bare = stdio server; `serve`/`version` subcommands); `python -m whoreps_mcp`.
- `.env.example`; 4 tests incl. a real MCP stdio handshake. Ruff clean.

### Scaffold
- Initial spec, build plan, and project docs.
