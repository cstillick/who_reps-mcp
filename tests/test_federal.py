"""M2: state + CD -> the correct federal officials, normalized."""

from __future__ import annotations

from pathlib import Path

import yaml

from whoreps_mcp.sources.federal import officials_for

FIXTURES = Path(__file__).parent / "fixtures"
ROSTER = yaml.safe_load((FIXTURES / "legislators_sample.yaml").read_text())
AS_OF = "2026-01-01"


def test_ok5_returns_two_senators_and_the_representative() -> None:
    officials = officials_for("OK", "5", ROSTER, AS_OF)
    by_office = {o.office: o for o in officials}
    assert sorted(by_office) == ["U.S. Representative", "U.S. Senator"]
    senators = [o for o in officials if o.office == "U.S. Senator"]
    assert {o.name for o in senators} == {"James Lankford", "Markwayne Mullin"}

    rep = next(o for o in officials if o.office == "U.S. Representative")
    assert rep.name == "Stephanie I. Bice"
    assert rep.district == "5"
    assert rep.party == "Republican"
    assert rep.website == "https://bice.house.gov"
    assert rep.term_end == "2027-01-03"
    assert rep.source == "unitedstates/congress-legislators"
    assert rep.photo_url.endswith("B001302.jpg")


def test_dc_has_a_delegate_and_no_senators() -> None:
    officials = officials_for("DC", "98", ROSTER, AS_OF)
    assert not any(o.office == "U.S. Senator" for o in officials)
    delegate = next(o for o in officials if o.level == "federal")
    assert delegate.office == "U.S. Delegate"
    assert delegate.name == "Eleanor Holmes Norton"


def test_wrong_district_returns_no_representative() -> None:
    officials = officials_for("OK", "1", ROSTER, AS_OF)
    # Senators are statewide, but there's no OK-1 rep in the sample.
    assert all(o.office != "U.S. Representative" for o in officials)
    assert len([o for o in officials if o.office == "U.S. Senator"]) == 2
