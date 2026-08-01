"""Inference pipeline exceptions."""


class InferenceError(Exception):
    """Base exception for all inference operations."""


class ModelLoadError(InferenceError):
    """Failed to load or initialize a model."""


class ModelNotFoundError(InferenceError):
    """Requested model is not available."""


class InferenceTimeoutError(InferenceError):
    """Model inference timed out."""


class DeviceError(InferenceError):
    """Requested compute device is not available."""
