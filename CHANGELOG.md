# Changelog

All notable changes to this project will be documented here.

## [Unreleased]

### M0 — Scaffold
- `pyproject.toml` (uv, hatchling, src layout); package `whoreps_mcp` with `sources/` subpackage.
- Typed `Settings` (optional `OPENSTATES_API_KEY` / `CONGRESS_GOV_API_KEY`, `CACHE_PATH`); pydantic models (`GeoResult`, `Official`, `OfficialsResponse`).
- FastMCP server with `ping`; `whoreps-mcp` entry point (bare = stdio server; `serve`/`version` subcommands); `python -m whoreps_mcp`.
- `.env.example`; 4 tests incl. a real MCP stdio handshake. Ruff clean.

### Scaffold
- Initial spec, build plan, and project docs.
