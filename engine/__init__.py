"""Descombinator Pro processing layer.

This package contains the processing layer of the application, including:
- Demucs: Separation backend with lazy loading for performance
- Export: Result export and file writing with batch support
- Inference: Model inference pipeline with multiple backends
- Audio: Audio loading, processing, and DSP operations
- Performance: Profiling, monitoring, and runtime optimization
"""

__all__ = [
    # Audio
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
    # Demucs
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
    # Export
    "BatchExporter",
    "ExportConfig",
    "ExportError",
    "ExportFormat",
    "ExportMetadata",
    "MetadataEmbedder",
    "UnsupportedFormatError",
    "WriteError",
    # Inference
    "DeviceError",
    "DeviceType",
    "DemucsAgent",
    "InferenceConfig",
    "InferenceError",
    "InferencePipeline",
    "InferenceTimeoutError",
    "ModelLoadError",
    "ModelManager",
    "ModelName",
    "ModelNotFoundError",
    "OpenUnmixAgent",
    "SeparationModel",
    # Performance
    "ResourceMonitor",
    "ResourceSnapshot",
    "TorchRuntimeOptimizer",
    "cpu_profile",
    "torch_profile_trace",
    "ThermalMonitor",
    "ThermalSnapshot",
    "ThermalState",
]
