# Python API Reference

Auto-generated API documentation from inline docstrings.

## Modules

### Audio Processing

- `engine.audio.loader` — Async audio file loading
- `engine.audio.resampler` — Audio resampling
- `engine.audio.postprocessor` — Post-processing effects
- `engine.audio.metadata` — Metadata reading/writing
- `engine.audio.errors` — Audio-specific exceptions

### Separation Engine

- `engine.demucs.separator` — Demucs separation backend
- `engine.demucs.config` — Demucs configuration
- `engine.inference.pipeline` — Inference pipeline
- `engine.inference.config` — Inference configuration

### Export Pipeline

- `engine.export.writer` — Audio file writing
- `engine.export.metadata` — Metadata embedding
- `engine.export.config` — Export configuration

### Performance

- `engine.performance.monitor` — Performance monitoring
- `engine.performance.profiler` — Profiling utilities

### Application

- `app.main_window` — Main application window
- `app.controllers.main_controller` — Main UI controller
- `app.controllers.playback_controller` — Playback controller
- `app.controllers.settings_controller` — Settings controller
- `app.services.separation_service` — Separation orchestration
- `app.services.playback_service` — Playback orchestration
- `app.models.app_state` — Application state model
- `app.models.settings_model` — Settings model

## Usage

This API reference is auto-generated from the source code docstrings using `mkdocstrings`.

To generate locally:

```bash
pip install -e ".[docs]"
mkdocs build
```

The API documentation will be available at `site/api/python.html`.
