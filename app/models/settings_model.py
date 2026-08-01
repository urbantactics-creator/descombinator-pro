"""Settings model."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from engine.export.config import ExportFormat
from engine.inference.config import ModelName


class SettingsModel(BaseModel):
    """Application settings model."""

    output_dir: Path = Field(default=Path.home() / "Music" / "Descombinator")
    default_model: ModelName = Field(default=ModelName.HTDEMUCS_FT)
    default_format: ExportFormat = Field(default=ExportFormat.WAV)
    theme: str = Field(default="dark")
