"""FastMCP server for whoreps.

M0 registers a health check (`ping`). The real tools — `lookup_officials`,
`list_districts`, `lookup_by_district`, `get_official_details` — are registered
here as later milestones land. Run with `whoreps-mcp` (bare) or `whoreps-mcp serve`.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from whoreps_mcp import service

mcp = FastMCP("whoreps")


@mcp.tool()
def ping() -> str:
    """Health check. Returns 'pong' if the server is alive."""
    return "pong"


@mcp.tool()
def lookup_officials(address: str) -> dict:
    """Who represents this address? Returns U.S. Senators + House member (and,
    where available, Governor + state legislators), each with party, contact,
    term, source, and as-of date, plus the OCD divisions and coverage notes."""
    resp = service.lookup_officials(address)
    return {"summary": service.summarize(resp), **resp.model_dump()}


@mcp.tool()
def list_districts(address: str) -> dict:
    """Just the districts/divisions for an address (the piece Google's Divisions
    API still gives) — congressional + state-legislative districts and OCD-IDs."""
    return service.list_districts(address)


@mcp.tool()
def lookup_by_district(state: str, chamber: str, district: str | None = None) -> dict:
    """Officials for a chamber + district, skipping geocoding. `chamber` is
    senate|house (federal) or upper|lower (state legislature)."""
    officials = service.lookup_by_district(state, chamber, district)
    return {"count": len(officials), "officials": [o.model_dump() for o in officials]}


@mcp.tool()
def get_official_details(official_id: str) -> dict:
    """Enriched detail for one official (committees + full contact where
    available), by the id returned from the other tools."""
    return service.get_official_details(official_id)


def run_stdio() -> None:
    """Run the MCP server over stdio (the default transport)."""
    mcp.run()


if __name__ == "__main__":
    run_stdio()
