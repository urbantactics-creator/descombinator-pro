"""Inference pipeline exceptions."""


class InferenceError(Exception):
    """Base exception for all inference operations."""


class ModelLoadError(InferenceError):
    """Failed to load or initialize a model."""


class ModelNotFoundError(InferenceError):
    """Requested model is not available."""


class InferenceTimeoutError(InferenceError):
    """Model inference timed out."""


# Default inference timeout in seconds. Used by pipeline.run() to guard
# against model inference hanging indefinitely in asyncio.to_thread.
DEFAULT_INFERENCE_TIMEOUT: float = 600.0  # 10 minutes


class DeviceError(InferenceError):
    """Requested compute device is not available."""
