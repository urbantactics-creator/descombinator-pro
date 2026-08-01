"""Audio processing exceptions."""


class AudioError(Exception):
    """Base exception for all audio operations."""


class AudioLoadError(AudioError):
    """Failed to load audio file."""


class AudioFormatError(AudioError):
    """Unsupported or corrupted audio format."""


class ResampleError(AudioError):
    """Resampling failed."""


class PreprocessingError(AudioError):
    """Audio preprocessing failed."""


class PostprocessingError(AudioError):
    """Audio postprocessing failed."""


class MetadataError(AudioError):
    """Metadata read/write failed."""


class AudioFileNotFoundError(AudioError):
    """Audio file does not exist."""
