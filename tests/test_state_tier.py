"""M4: governor + state legislators merge in, and gaps degrade with notes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from whoreps_mcp import service
from whoreps_mcp.cache import Cache
from whoreps_mcp.config import get_settings
from whoreps_mcp.sources import governors
from whoreps_mcp.sources.openstates import parse_people

FIXTURES = Path(__file__).parent / "fixtures"
ROSTER = yaml.safe_load((FIXTURES / "legislators_sample.yaml").read_text())
OPENSTATES_OK = json.loads((FIXTURES / "openstates_ok.json").read_text())
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


def test_governor_lookup() -> None:
    gov = governors.governor_for("OK")
    assert gov is not None
    assert gov.name == "Kevin Stitt"
    assert gov.office == "Governor"
    assert gov.chamber == "executive"
    assert gov.as_of  # carries the snapshot freshness date
    assert governors.governor_for("DC") is None


def test_parse_openstates_people() -> None:
    officials = parse_people(OPENSTATES_OK, AS_OF)
    offices = {o.office for o in officials}
    assert offices == {"State Senator", "State Representative"}
    sen = next(o for o in officials if o.office == "State Senator")
    assert sen.district == "48"
    assert sen.chamber == "upper"
    assert sen.phone == "405-521-5500"
    assert sen.level == "state"


def test_full_slate_for_ok5() -> None:
    resp = service.lookup_officials(
        OK5, legislators=ROSTER, openstates_payload=OPENSTATES_OK, as_of=AS_OF
    )
    offices = [o.office for o in resp.officials]
    assert offices.count("U.S. Senator") == 2
    assert "U.S. Representative" in offices
    assert "Governor" in offices
    assert "State Senator" in offices and "State Representative" in offices
    assert resp.coverage_notes == []  # OK is fully covered


def test_dc_degrades_with_notes() -> None:
    resp = service.lookup_officials(DC, legislators=ROSTER, as_of=AS_OF)
    joined = " ".join(resp.coverage_notes)
    assert "no U.S. Senators" in joined
    assert "Mayor, not a Governor" in joined
    assert "no state legislature" in joined
    # Still returns the federal delegate despite the gaps.
    assert any(o.office == "U.S. Delegate" for o in resp.officials)


def test_missing_openstates_key_notes_omission() -> None:
    # No key, no injected payload -> state legislators omitted with a note.
    resp = service.lookup_officials(OK5, legislators=ROSTER, as_of=AS_OF)
    assert any("OPENSTATES_API_KEY" in n for n in resp.coverage_notes)
    assert not any(
        o.level == "state" and "Senator" in o.office and o.office.startswith("State")
        for o in resp.officials
    )
    # Governor still included (vendored, no key needed).
    assert any(o.office == "Governor" for o in resp.officials)
