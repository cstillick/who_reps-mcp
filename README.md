# whoreps-mcp

**Address → your elected officials, as an MCP server.** A free, open replacement for the Google Civic Information *Representatives API*, which was shut down on April 30, 2025 and left a generation of civic apps broken.

Give it a U.S. street address and it returns the people who represent that address — U.S. Senators, U.S. House member, Governor, and state legislators — by stitching together free public data sources that Google's turndown left stranded.

## Why this exists

Google's Representatives API (`representativeInfoByAddress`) was the default way to answer "who represents me?" When Google killed it, the official guidance was: use our Divisions API to get an OCD division ID, then *go buy* officeholder data from BallotReady, Cicero, or Ballotpedia. This MCP rebuilds the free path: **address → districts (Census) → officials (open congressional + state legislator data).**

## What it does

MCP tools exposed to any compatible client (Claude, Cursor, etc.):

- `lookup_officials(address)` — the headline tool. Address in, full slate of officials out.
- `lookup_by_district(state, chamber, district)` — skip geocoding if you already know the district.
- `get_official_details(official_id)` — contact info, party, term, committees where available.
- `list_districts(address)` — just the district/division IDs for an address (the piece Google still gives, but free and self-hosted).

## Status

Scaffold / planning. See `SPEC.md` for the design and `BUILD_PLAN.md` for the milestone-by-milestone build order. `CLAUDE.md` is the working brief for Claude Code.

## Quick start (target state)

```bash
uv sync                      # or: pip install -e .
cp .env.example .env         # add free API keys
uv run whoreps-mcp           # runs the MCP server over stdio
```

## License

MIT (intended — keeps it adoptable, which is the point).
