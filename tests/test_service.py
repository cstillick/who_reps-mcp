"""M3: lookup_officials wires geocode -> federal roster -> OfficialsResponse."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from whoreps_mcp import service
from whoreps_mcp.cache import Cache
from whoreps_mcp.config import get_settings

FIXTURES = Path(__file__).parent / "fixtures"
ROSTER = yaml.safe_load((FIXTURES / "legislators_sample.yaml").read_text())
AS_OF = "2026-01-01"

OK5 = "2300 N Lincoln Blvd, Oklahoma City, OK 73105"
DC = "1600 Pennsylvania Ave NW, Washington, DC 20500"


@pytest.fixture(autouse=True)
def _seed_geocode_cache():
    cache = Cache(get_settings())
    cache.set(
        f"census:onelineaddress:{OK5.lower()}",
        json.loads((FIXTURES / "census_ok5.json").read_text()),
    )
    cache.set(
        f"census:onelineaddress:{DC.lower()}", json.loads((FIXTURES / "census_dc.json").read_text())
    )


def test_lookup_federal_slate_for_ok5() -> None:
    resp = service.lookup_officials(OK5, legislators=ROSTER, as_of=AS_OF)
    names = {o.name for o in resp.officials}
    # The federal slate is present (governor is added by the state tier, M4).
    assert {"James Lankford", "Markwayne Mullin", "Stephanie I. Bice"} <= names
    assert "ocd-division/country:us/state:ok/cd:5" in resp.divisions

    summary = service.summarize(resp)
    assert "U.S. Representative Stephanie I. Bice" in summary
    assert "U.S. Senator James Lankford" in summary


def test_lookup_dc_degrades_with_notes() -> None:
    resp = service.lookup_officials(DC, legislators=ROSTER, as_of=AS_OF)
    assert not any(o.office == "U.S. Senator" for o in resp.officials)
    assert any(o.office == "U.S. Delegate" for o in resp.officials)
    joined = " ".join(resp.coverage_notes)
    assert "no U.S. Senators" in joined
    assert "no state legislature" in joined


def test_list_districts_returns_divisions() -> None:
    out = service.list_districts(OK5)
    assert out["congressional_district"] == "5"
    assert out["state"] == "OK"
    assert "ocd-division/country:us/state:ok/cd:5" in out["divisions"]
