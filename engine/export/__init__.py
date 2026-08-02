"""Result export and file writing.

Heavy module imports (soundfile, mutagen) are deferred with PEP 562
``__getattr__`` so importing ``engine.export`` does not load them.
``config`` and ``errors`` stay eager.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

from engine.export.config import ExportConfig, ExportFormat, ExportMetadata
from engine.export.errors import (
    ExportError,
    MetadataError,
    UnsupportedFormatError,
    WriteError,
)

if TYPE_CHECKING:
    from engine.export.batch_exporter import BatchExporter
    from engine.export.metadata import MetadataEmbedder
    from engine.export.writer import ExportWriter

_LAZY = {
    "BatchExporter": "engine.export.batch_exporter",
    "ExportWriter": "engine.export.writer",
    "MetadataEmbedder": "engine.export.metadata",
}


def __getattr__(name: str) -> Any:
    """Resolve lazy attributes on demand (PEP 562)."""
    if name in _LAZY:
        return getattr(importlib.import_module(_LAZY[name]), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "BatchExporter",
    "ExportConfig",
    "ExportFormat",
    "ExportMetadata",
    "ExportError",
    "MetadataError",
    "UnsupportedFormatError",
    "WriteError",
    "MetadataEmbedder",
    "ExportWriter",
]
