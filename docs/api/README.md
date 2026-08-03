# API Reference

This section provides API reference documentation for Descombinator Pro's public interfaces.

## Overview

The API is organized into three layers:

1. **Engine Layer** (`engine/`) — Processing layer with no UI dependencies
2. **Service Layer** (`app/services/`) — Orchestration layer coordinating between app and engine
3. **Presentation Layer** (`app/`) — UI components, controllers, and widgets

## Engine API

### Audio Processing

- [AudioLoader](engine/audio/loader.md) — Async audio file loading with format detection
- [AudioResampler](engine/audio/resampler.md) — High-quality audio resampling
- [AudioPreprocessor](engine/audio/preprocessor.md) — DC offset removal and normalization
- [AudioPostprocessor](engine/audio/postprocessor.md) — Artifact reduction and peak limiting
- [MetadataReader](engine/audio/metadata.md) — Read audio file metadata
- [MetadataWriter](engine/audio/metadata.md) — Write audio file metadata

### Inference

- [DemucsAgent](engine/inference/demucs_agent.md) — Demucs separation model agent
- [OpenUnmixAgent](engine/inference/openunmix_agent.md) — Open-Unmix separation model agent
- [InferencePipeline](engine/inference/pipeline.md) — Full inference pipeline orchestration
- [ModelManager](engine/inference/model_manager.md) — Model lifecycle management with caching

### Separation

- [DemucsSeparator](engine/demucs/separator.md) — Full separation workflow orchestration

### Export

- [ExportWriter](engine/export/writer.md) — Multi-format audio file writing
- [BatchExporter](engine/export/batch_exporter.md) — Batch export with progress tracking

### Performance

- [ResourceMonitor](engine/performance/monitor.md) — System resource monitoring
- [ThermalMonitor](engine/performance/thermal.md) — Cross-platform CPU/GPU temperature monitoring
- [cpu_profile / torch_profile_trace](engine/performance/profiler.md) — Profiling context managers
- [TorchRuntimeOptimizer](engine/performance/optimizer.md) — PyTorch runtime optimization

## Service API

- [SeparationService](app/services/separation_service.md) — Separation pipeline orchestration
- [PlaybackService](app/services/playback_service.md) — Audio playback orchestration
- [PlaybackStateStore](app/services/playback_state_store.md) — Playback state persistence
- [ExportService](app/services/export_service.md) — Export pipeline orchestration

## Data Models

- [AppState](app/models/app_state.md) — Application state model
- [SettingsModel](app/models/settings_model.md) — User settings model
- [InferenceConfig](engine/inference/config.md) — Inference configuration
- [SeparationConfig](engine/demucs/config.md) — Separation configuration
- [ExportConfig](engine/export/config.md) — Export configuration
- [SeparationResult](app/models/separation_result.md) — Separation result model
- [AudioMetadata](engine/audio/metadata.md) — Audio metadata model

## Enums

- [SeparationStatus](app/models/app_state.md) — Separation workflow states
- [SeparationState](engine/demucs/separator.md) — Separation workflow states
- [ThermalState](engine/performance/thermal.md) — Thermal thresholds state machine
- [ModelName](engine/inference/config.md) — Available separation models
- [DeviceType](engine/inference/config.md) — Compute device types
- [ExportFormat](engine/export/config.md) — Supported export formats

## Error Hierarchy

- [Audio Errors](engine/audio/errors.md) — Audio processing exceptions
- [Inference Errors](engine/inference/errors.md) — Inference pipeline exceptions
- [Separation Errors](engine/demucs/errors.md) — Separation workflow exceptions
- [Export Errors](engine/export/errors.md) — Export pipeline exceptions

## Generating API Documentation

API reference is generated from docstrings using [pdoc](https://pdoc.dev/):

```bash
# Install pdoc
pip install pdoc

# Generate API documentation
pdoc --html -o docs/api engine/ app/

# Serve locally for development
pdoc -o docs/api engine/ app/
```

## Inline Documentation Standards

All public modules, classes, and methods follow these documentation standards:

```python
"""Module-level docstring describing the module's purpose.

Example:
    >>> loader = AudioLoader()
    >>> audio = await loader.load(Path("song.mp3"))
"""

class ClassName:
    """Class-level docstring describing the class's purpose.

    Attributes:
        attribute_name: Description of the attribute.
    """

    def method_name(self, param: type) -> return_type:
        """Method-level docstring.

        Args:
            param: Description of the parameter.

        Returns:
            Description of the return value.

        Raises:
            ExceptionType: When the exception occurs.
        """
```
