# whoreps-mcp

**Address → your elected officials, as an MCP server.** A free, open replacement
for the Google Civic Information *Representatives API*, which was shut down on
April 30, 2025 and left a generation of civic apps broken.

Give it a U.S. street address and it returns the people who represent it — U.S.
Senators, U.S. House member, Governor, and state legislators — by stitching
together free public data: **address → districts (Census) → officials (open
congressional + state-legislator data).**

## Why this exists

When Google killed `representativeInfoByAddress`, the official guidance was: use
our Divisions API for an OCD id, then *go buy* officeholder data from BallotReady,
Cicero, or Ballotpedia. This rebuilds the free path so an agent can just answer
"who represents this address?"

## Quick start

The **federal tier needs no API keys** — the Census geocoder and the
`unitedstates/congress-legislators` dataset are both free and key-less.

```bash
uv sync

# As an MCP server (stdio):
uv run whoreps-mcp

# Or try the data path from a terminal (no keys needed):
uv run whoreps-mcp lookup "1600 Pennsylvania Ave NW, Washington, DC 20500"
uv run whoreps-mcp lookup "2300 N Lincoln Blvd, Oklahoma City, OK 73105"
#  4 officials for 2300 N LINCOLN BLVD, ...: U.S. Senator James Lankford (R);
#  U.S. Senator Markwayne Mullin (R); U.S. Representative Stephanie I. Bice (R, 5);
#  Governor Kevin Stitt (R). State legislators omitted — set OPENSTATES_API_KEY ...
```

To add the **state-legislator tier**, get a free
[OpenStates key](https://openstates.org/accounts/profile/), `cp .env.example .env`,
set `OPENSTATES_API_KEY`, and the same lookups will include state senators and
representatives.

## Use it as an MCP server

```json
{
  "mcpServers": {
    "whoreps": {
      "command": "uv",
      "args": ["run", "whoreps-mcp"],
      "cwd": "/path/to/whoreps-mcp"
    }
  }
}
```

### Tools

| Tool | What it does |
|---|---|
| `lookup_officials(address)` | The headline tool. Address in, full slate out (federal + state where available), each official with party, contact, term, source, and as-of date, plus OCD divisions and coverage notes. |
| `list_districts(address)` | Just the districts/divisions for an address — congressional + state-legislative districts and OCD-IDs (the piece Google's Divisions API gave, free and self-hosted). |
| `lookup_by_district(state, chamber, district)` | Skip geocoding: `senate`/`house` (federal) or `upper`/`lower` (state). |
| `get_official_details(official_id)` | Enriched detail for one official — committees + full contact where available. |

Each tool returns structured JSON plus a concise text summary.

## Graceful degradation

This is a civic tool, so correctness and honesty matter:

- **Federal always works**, with zero keys. Missing tiers never fail the whole
  request — you get what's available plus `coverage_notes` explaining any gap.
- **DC and territories** return the non-voting delegate (no senators), and note
  that DC has a Mayor rather than a Governor and no state legislature.
- **Bad/PO-box/new-construction addresses** that don't geocode return an empty
  result with a note, not an error.
- **Freshness is visible.** Every official carries its `source` and `as_of` date.
  Governors are a vendored, dated snapshot (see [docs/governors.md](docs/governors.md));
  everything else is fetched live and cached.

## How it works

```
address ─▶ Census geocoder ─▶ {lat/lon, congressional district, state-leg districts, OCD divisions}
                                     │
              ┌──────────────────────┼───────────────────────┐
              ▼                      ▼                         ▼
     congress-legislators     OpenStates people.geo      governors.json
     (U.S. Senate + House)    (state legislators)        (vendored)
              └──────────────────────┼───────────────────────┘
                                     ▼
                     merge + normalize -> OfficialsResponse  (SQLite-cached)
```

Sources live behind `sources/` so the whole flow is tested against recorded
fixtures — CI is fully offline.

## Development

```bash
uv run pytest        # offline suite (recorded fixtures)
uv run ruff check .  # lint
```

If `uv run whoreps-mcp` ever reports `No module named 'whoreps_mcp'` (a known
editable-install quirk on some setups, e.g. paths with spaces), run with
`PYTHONPATH=src uv run whoreps-mcp ...`.

See [SPEC.md](SPEC.md) and [BUILD_PLAN.md](BUILD_PLAN.md) for the design.

## License

MIT.
