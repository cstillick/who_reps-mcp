"""Pydantic models for officials, geocoding, and the tool responses."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Level = Literal["federal", "state"]
Chamber = Literal["upper", "lower", "executive"]


class GeoResult(BaseModel):
    """Output of geocoding an address into districts + divisions."""

    matched_address: str
    lat: float
    lon: float
    state: str  # USPS code, e.g. "OK"
    state_fips: str | None = None
    congressional_district: str | None = None  # e.g. "5" ("00" for at-large)
    state_leg_districts: dict[str, str] = Field(default_factory=dict)  # {"upper": .., "lower": ..}
    divisions: list[str] = Field(default_factory=list)  # OCD-IDs


class Official(BaseModel):
    id: str  # stable id, e.g. "us_senate:OK:lankford" or an OpenStates ocd id
    name: str
    office: str  # "U.S. Senator", "State Representative", ...
    level: Level
    chamber: Chamber | None = None
    district: str | None = None
    party: str | None = None
    phone: str | None = None
    website: str | None = None
    photo_url: str | None = None
    term_end: str | None = None
    source: str  # which dataset
    as_of: str  # ISO date the source data was current


class OfficialsResponse(BaseModel):
    matched_address: str
    divisions: list[str] = Field(default_factory=list)
    officials: list[Official] = Field(default_factory=list)
    coverage_notes: list[str] = Field(default_factory=list)
