"""M5: get_official_details + lookup_by_district."""

from __future__ import annotations

from pathlib import Path

import yaml

from whoreps_mcp import service

FIXTURES = Path(__file__).parent / "fixtures"
ROSTER = yaml.safe_load((FIXTURES / "legislators_sample.yaml").read_text())
AS_OF = "2026-01-01"


def test_details_for_federal_representative() -> None:
    d = service.get_official_details("us_house:OK-5:B001302", legislators=ROSTER, as_of=AS_OF)
    assert d["name"] == "Stephanie I. Bice"
    assert d["office"] == "U.S. Representative"
    assert d["district"] == "5"
    assert d["committees"] == []  # no Congress.gov key -> base detail


def test_details_for_senator_and_governor() -> None:
    sen = service.get_official_details("us_senate:OK:L000575", legislators=ROSTER, as_of=AS_OF)
    assert sen["name"] == "James Lankford"
    gov = service.get_official_details("governor:OK")
    assert gov["name"] == "Kevin Stitt"
    assert gov["office"] == "Governor"


def test_details_unknown_id() -> None:
    assert service.get_official_details("us_senate:OK:ZZZ", legislators=ROSTER)["found"] is False
    assert service.get_official_details("nonsense")["found"] is False


def test_lookup_by_district_federal() -> None:
    senators = service.lookup_by_district("OK", "senate", legislators=ROSTER, as_of=AS_OF)
    assert {o.name for o in senators} == {"James Lankford", "Markwayne Mullin"}

    house = service.lookup_by_district("OK", "house", "5", legislators=ROSTER, as_of=AS_OF)
    assert [o.name for o in house] == ["Stephanie I. Bice"]


def test_lookup_by_district_state_degrades_without_key() -> None:
    # No OpenStates key configured in tests -> empty (graceful), not an error.
    assert service.lookup_by_district("OK", "upper", "48") == []
