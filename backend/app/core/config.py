"""
SOMA Application Configuration.

Loads settings from environment variables (populated via .env file).
Uses Pydantic Settings for validation and type coercion.
"""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the SOMA backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Environment ──────────────────────────────────────────
    env: str = "development"

    # ── Data directory paths ─────────────────────────────────
    data_raw_dir: Path = Path("/app/data/raw")
    data_processed_dir: Path = Path("/app/data/processed")
    data_exports_dir: Path = Path("/app/data/exports")

    # ── API configuration ────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # ── Processing defaults ──────────────────────────────────
    default_speckle_filter_window: int = 5
    default_cpr_averaging_window: int = 3
    default_roughness_window: int = 5
    default_cost_map_resolution_m: float = 5.0

    # ── Derived sub-paths (not from env, computed once) ──────
    @property
    def dfsar_dir(self) -> Path:
        return self.data_raw_dir / "dfsar"

    @property
    def ohrc_dir(self) -> Path:
        return self.data_raw_dir / "ohrc"

    @property
    def dem_dir(self) -> Path:
        return self.data_raw_dir / "dem"

    @property
    def radar_output_dir(self) -> Path:
        return self.data_processed_dir / "radar"

    @property
    def terrain_output_dir(self) -> Path:
        return self.data_processed_dir / "terrain"

    @property
    def ice_output_dir(self) -> Path:
        return self.data_processed_dir / "ice"

    @property
    def landing_sites_output_dir(self) -> Path:
        return self.data_processed_dir / "landing_sites"

    @property
    def traverses_output_dir(self) -> Path:
        return self.data_processed_dir / "traverses"


# Singleton — import this everywhere
settings = Settings()
