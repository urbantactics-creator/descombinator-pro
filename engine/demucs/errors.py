"""Separation engine exceptions."""


class SeparationError(Exception):
    """Base exception for all separation operations."""

    def __init__(self, message: str = "Separation operation failed") -> None:
        super().__init__(message)


class ModelLoadError(SeparationError):
    """Failed to load or initialize a model."""

    def __init__(self, message: str = "Model loading failed") -> None:
        super().__init__(message)


class InferenceError(SeparationError):
    """Inference operation failed during separation."""

    def __init__(self, message: str = "Inference operation failed") -> None:
        super().__init__(message)


class ProcessingError(SeparationError):
    """Audio processing failed during separation."""

    def __init__(self, message: str = "Audio processing failed") -> None:
        super().__init__(message)


class InvalidAudioError(SeparationError):
    """Input audio is invalid or unsupported."""

    def __init__(self, message: str = "Invalid audio input") -> None:
        super().__init__(message)
