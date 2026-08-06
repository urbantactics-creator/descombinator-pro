"""Export pipeline exceptions."""

from __future__ import annotations


class ExportError(Exception):
    """Base exception for all export operations."""


class UnsupportedFormatError(ExportError):
    """Requested export format is not supported."""


class WriteError(ExportError):
    """Failed to write export file."""


class MetadataError(ExportError):
    """Metadata embedding failed."""
