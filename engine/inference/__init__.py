"""Model inference pipeline.

Heavy module imports (torch, demucs, openunmix) are deferred with PEP 562
``__getattr__`` so importing ``engine.inference`` does not load them.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

from engine.inference.config import DeviceType, InferenceConfig, ModelName
from engine.inference.errors import (
    DeviceError,
    InferenceError,
    InferenceTimeoutError,
    ModelLoadError,
    ModelNotFoundError,
)

if TYPE_CHECKING:
    from engine.inference.demucs_agent import DemucsAgent
    from engine.inference.model_manager import ModelManager, SeparationModel
    from engine.inference.openunmix_agent import OpenUnmixAgent
    from engine.inference.pipeline import InferencePipeline

_LAZY = {
    "DemucsAgent": "engine.inference.demucs_agent",
    "InferencePipeline": "engine.inference.pipeline",
    "ModelManager": "engine.inference.model_manager",
    "OpenUnmixAgent": "engine.inference.openunmix_agent",
    "SeparationModel": "engine.inference.model_manager",
}


def __getattr__(name: str) -> Any:
    """Resolve lazy attributes on demand (PEP 562)."""
    if name in _LAZY:
        return getattr(importlib.import_module(_LAZY[name]), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "DeviceError",
    "DeviceType",
    "DemucsAgent",
    "InferenceConfig",
    "InferenceError",
    "InferencePipeline",
    "InferenceTimeoutError",
    "ModelLoadError",
    "ModelManager",
    "ModelName",
    "ModelNotFoundError",
    "OpenUnmixAgent",
    "SeparationModel",
]
