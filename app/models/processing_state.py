"""Processing state enumeration."""

from enum import StrEnum


class ProcessingState(StrEnum):
    """Processing workflow states."""

    IDLE = "idle"
    LOADING = "loading"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"
    CANCELLED = "cancelled"
