"""M0 smoke tests: models, CLI, and a real MCP stdio handshake."""

from __future__ import annotations

import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typer.testing import CliRunner

from whoreps_mcp.cli import app
from whoreps_mcp.models import GeoResult, Official, OfficialsResponse

runner = CliRunner()


def test_cli_version() -> None:
    res = runner.invoke(app, ["version"])
    assert res.exit_code == 0
    assert "whoreps-mcp" in res.output


def test_models_roundtrip() -> None:
    geo = GeoResult(
        matched_address="1600 Pennsylvania Ave NW, Washington, DC 20500",
        lat=38.8977,
        lon=-77.0365,
        state="DC",
        congressional_district="98",
        divisions=["ocd-division/country:us/district:dc"],
    )
    off = Official(
        id="us_senate:OK:lankford",
        name="James Lankford",
        office="U.S. Senator",
        level="federal",
        party="Republican",
        source="congress-legislators",
        as_of="2026-01-01",
    )
    resp = OfficialsResponse(
        matched_address=geo.matched_address, divisions=geo.divisions, officials=[off]
    )
    assert resp.officials[0].level == "federal"
    assert geo.state == "DC"


def test_server_ping_direct() -> None:
    from whoreps_mcp.server import ping

    assert ping() == "pong"


def test_server_stdio_handshake() -> None:
    async def go():
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "whoreps_mcp", "serve"],
            env={**os.environ, "PYTHONPATH": "src"},
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                assert "ping" in {t.name for t in tools.tools}
                result = await session.call_tool("ping", {})
                text = "".join(b.text for b in result.content if b.type == "text")
                assert "pong" in text

    asyncio.run(go())
