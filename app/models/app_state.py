"""Application state model."""

from pathlib import Path

from pydantic import BaseModel, Field

from app.models.processing_state import ProcessingState
from app.models.settings_model import SettingsModel


class AppState(BaseModel):
    """Application state model."""

    current_file: Path | None = None
    processing_status: ProcessingState = Field(default=ProcessingState.IDLE)
    selected_stems: list[str] = Field(default_factory=lambda: ["vocals", "other"])
    settings: SettingsModel = Field(default_factory=SettingsModel)
