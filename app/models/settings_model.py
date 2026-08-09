"""Settings model."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from engine.export.config import ExportFormat
from engine.inference.config import ModelName


class SettingsModel(BaseModel):
    """Application settings model."""

    model_config = ConfigDict(use_enum_values=True)

    output_dir: Path = Field(default=Path.home() / "Music" / "Descombinator")
    default_model: ModelName = Field(default=ModelName.HTDEMUCS_FT)
    default_format: ExportFormat = Field(default=ExportFormat.WAV)
    theme: str = Field(default="dark")
    reduced_motion: bool = False
    high_contrast: bool = False
    segment: int | None = None
    mixed_precision: bool = False
    pin_memory: bool = False
    sample_rate: int = Field(default=44100, ge=8000, le=192000)
    bit_depth: int = Field(default=16, ge=8, le=32)
    bitrate: int = Field(default=192000, ge=32000, le=320000)
    normalize: bool = True
    fade_in: float = Field(default=0.0, ge=0.0, le=10.0)
    fade_out: float = Field(default=0.0, ge=0.0, le=10.0)
