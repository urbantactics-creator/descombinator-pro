"""Inference configuration models."""

from enum import StrEnum

from pydantic import BaseModel, Field


class ModelName(StrEnum):
    """Available separation models."""

    HTDEMUCS_FT = "htdemucs_ft"
    MDX_EXTRA = "mdx_extra"
    UMXHQ = "umxhq"


class DeviceType(StrEnum):
    """Compute device types."""

    CPU = "cpu"
    CUDA = "cuda"


class InferenceConfig(BaseModel):
    """Configuration for inference pipeline."""

    model_name: ModelName = ModelName.HTDEMUCS_FT
    device: DeviceType = DeviceType.CPU
    shifts: int = Field(default=1, ge=0, le=10)
    overlap: float = Field(default=0.25, ge=0.0, le=1.0)
    segment: int | None = None
    jobs: int = Field(default=0, ge=0)
    mixed_precision: bool = False
    pin_memory: bool = False
    target_stems: list[str] = Field(default_factory=lambda: ["vocals", "other"])
