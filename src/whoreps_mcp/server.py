"""FastMCP server for whoreps.

M0 registers a health check (`ping`). The real tools — `lookup_officials`,
`list_districts`, `lookup_by_district`, `get_official_details` — are registered
here as later milestones land. Run with `whoreps-mcp` (bare) or `whoreps-mcp serve`.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("whoreps")


@mcp.tool()
def ping() -> str:
    """Health check. Returns 'pong' if the server is alive."""
    return "pong"


def run_stdio() -> None:
    """Run the MCP server over stdio (the default transport)."""
    mcp.run()


if __name__ == "__main__":
    run_stdio()
