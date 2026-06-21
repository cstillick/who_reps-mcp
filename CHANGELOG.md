# Changelog

All notable changes to this project will be documented here.

## [Unreleased]

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
