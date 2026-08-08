"""Audio loading and processing.

Heavy module imports (librosa, soundfile, mutagen, resampy) are deferred
with PEP 562 ``__getattr__`` so importing ``engine.audio`` does not load
them. ``errors`` and the numpy-only ``postprocessor`` stay eager.
"""

import importlib
from typing import TYPE_CHECKING, Any

from engine.audio.errors import (
    AudioError,
    AudioFileNotFoundError,
    AudioFormatError,
    AudioLoadError,
    MetadataError,
    PostprocessingError,
    PreprocessingError,
    ResampleError,
)
from engine.audio.postprocessor import AudioPostprocessor

if TYPE_CHECKING:
    from engine.audio.loader import AudioLoader
    from engine.audio.metadata import AudioMetadata, MetadataReader, MetadataWriter
    from engine.audio.preprocessor import AudioPreprocessor
    from engine.audio.resampler import AudioResampler

_LAZY = {
    "AudioLoader": "engine.audio.loader",
    "AudioMetadata": "engine.audio.metadata",
    "AudioPreprocessor": "engine.audio.preprocessor",
    "AudioResampler": "engine.audio.resampler",
    "MetadataReader": "engine.audio.metadata",
    "MetadataWriter": "engine.audio.metadata",
}


def __getattr__(name: str) -> Any:
    """Resolve lazy attributes on demand (PEP 562)."""
    if name in _LAZY:
        return getattr(importlib.import_module(_LAZY[name]), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AudioError",
    "AudioFileNotFoundError",
    "AudioFormatError",
    "AudioLoader",
    "AudioLoadError",
    "AudioMetadata",
    "AudioPostprocessor",
    "AudioPreprocessor",
    "AudioResampler",
    "MetadataError",
    "MetadataReader",
    "MetadataWriter",
    "PostprocessingError",
    "PreprocessingError",
    "ResampleError",
]
