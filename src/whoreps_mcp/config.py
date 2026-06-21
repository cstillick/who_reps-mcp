"""Typed configuration. Keys are optional — the federal tier needs none."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Keys (all optional / free) ---
    openstates_api_key: str | None = Field(default=None, validation_alias="OPENSTATES_API_KEY")
    congress_gov_api_key: str | None = Field(default=None, validation_alias="CONGRESS_GOV_API_KEY")

    # --- Cache ---
    cache_path: Path = Field(
        default=Path("./data/whoreps-cache.sqlite"), validation_alias="CACHE_PATH"
    )
    cache_ttl_seconds: int = 7 * 24 * 60 * 60  # districts/rosters change slowly

    # --- Endpoints ---
    census_base: str = "https://geocoding.geo.census.gov/geocoder"
    openstates_base: str = "https://v3.openstates.org"
    congress_gov_base: str = "https://api.congress.gov/v3"
    legislators_url: str = (
        "https://raw.githubusercontent.com/unitedstates/congress-legislators/"
        "main/legislators-current.yaml"
    )

    def ensure_dirs(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    return Settings()
