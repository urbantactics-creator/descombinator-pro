"""Processing state enumeration."""

from __future__ import annotations

from enum import StrEnum


class ProcessingState(StrEnum):
    """Processing workflow states."""

    IDLE = "idle"
    LOADING = "loading"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"
    CANCELLED = "cancelled"
