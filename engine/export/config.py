"""Export configuration model."""

from enum import StrEnum

from pydantic import BaseModel, Field


class ExportFormat(StrEnum):
    """Supported export formats."""

    WAV = "wav"
    FLAC = "flac"
    MP3 = "mp3"
    M4A = "m4a"


class ExportConfig(BaseModel):
    """Configuration for the export pipeline."""

    format: ExportFormat = ExportFormat.WAV
    sample_rate: int = Field(default=44100, ge=8000, le=192000)
    bit_depth: int = Field(default=16, ge=8, le=32)
    bitrate: int = Field(default=192000, ge=32000, le=320000)
    normalize: bool = True
    fade_in: float = Field(default=0.0, ge=0.0, le=10.0)
    fade_out: float = Field(default=0.0, ge=0.0, le=10.0)
    metadata: ExportMetadata | None = None


class ExportMetadata(BaseModel):
    """Metadata to embed in exported files."""

    title: str | None = None
    artist: str | None = None
    album: str | None = None
    genre: str | None = None
