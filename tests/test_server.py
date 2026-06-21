"""Integration: the MCP server boots over stdio and answers all tools.

Spawns `python -m whoreps_mcp serve` and drives it with the official MCP client.
The full lookup flow runs offline by pre-seeding the cache (geocode + roster),
exactly the data the server reads.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

import yaml
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from whoreps_mcp.cache import Cache
from whoreps_mcp.config import get_settings

FIXTURES = Path(__file__).parent / "fixtures"
TOOLS = {"ping", "lookup_officials", "list_districts", "lookup_by_district", "get_official_details"}
OK5 = "2300 N Lincoln Blvd, Oklahoma City, OK 73105"


def _payload(result) -> dict | str:
    text = "".join(b.text for b in result.content if b.type == "text")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _params() -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "whoreps_mcp", "serve"],
        env={**os.environ, "PYTHONPATH": "src"},
    )


def _seed_cache() -> None:
    cache = Cache(get_settings())
    cache.set(
        f"census:onelineaddress:{OK5.lower()}",
        json.loads((FIXTURES / "census_ok5.json").read_text()),
    )
    cache.set("federal:roster", yaml.safe_load((FIXTURES / "legislators_sample.yaml").read_text()))


def test_server_lists_all_tools(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("CACHE_PATH", str(tmp_path / "cache.sqlite"))

    async def go():
        async with stdio_client(_params()) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                assert TOOLS.issubset({t.name for t in tools.tools})
                assert "pong" in _payload(await session.call_tool("ping", {}))

    asyncio.run(go())


def test_server_lookup_flow_offline(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("CACHE_PATH", str(tmp_path / "cache.sqlite"))
    _seed_cache()  # writes to the same CACHE_PATH the subprocess will read

    async def go():
        async with stdio_client(_params()) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                resp = _payload(await session.call_tool("lookup_officials", {"address": OK5}))
                names = {o["name"] for o in resp["officials"]}
                assert {
                    "James Lankford",
                    "Markwayne Mullin",
                    "Stephanie I. Bice",
                    "Kevin Stitt",
                } <= names
                assert "summary" in resp

                districts = _payload(await session.call_tool("list_districts", {"address": OK5}))
                assert districts["congressional_district"] == "5"

                rep = next(o for o in resp["officials"] if o["office"] == "U.S. Representative")
                detail = _payload(
                    await session.call_tool("get_official_details", {"official_id": rep["id"]})
                )
                assert detail["name"] == "Stephanie I. Bice"

    asyncio.run(go())
