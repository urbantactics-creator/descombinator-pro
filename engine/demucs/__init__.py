"""Demucs separation backend.

Heavy module imports (torch, demucs) are deferred with PEP 562
``__getattr__`` so importing ``engine.demucs`` does not load them.
"""

import importlib
from typing import TYPE_CHECKING, Any

from engine.demucs.config import DeviceType, ModelName, SeparationConfig, SplitMode
from engine.demucs.errors import (
    InvalidAudioError,
    ModelLoadError,
    ProcessingError,
    SeparationError,
)

if TYPE_CHECKING:
    from engine.demucs.separator import DemucsSeparator, SeparationState

_LAZY = {
    "DemucsSeparator": "engine.demucs.separator",
    "SeparationState": "engine.demucs.separator",
}


def __getattr__(name: str) -> Any:
    """Resolve lazy attributes on demand (PEP 562)."""
    if name in _LAZY:
        return getattr(importlib.import_module(_LAZY[name]), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "DemucsSeparator",
    "DeviceType",
    "InvalidAudioError",
    "ModelLoadError",
    "ModelName",
    "ProcessingError",
    "SeparationConfig",
    "SeparationError",
    "SeparationState",
    "SplitMode",
]
