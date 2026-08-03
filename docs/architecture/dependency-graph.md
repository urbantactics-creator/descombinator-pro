# Dependency Graph

This document describes the dependency graph between modules in Descombinator Pro.

## Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    app/ (Presentation)                   │
│  ┌──────────┐  ┌──────────────┐  ┌────────────┐         │
│  │   ui/    │  │ controllers/ │  │  widgets/  │         │
│  └──────────┘  └──────────────┘  └────────────┘         │
│         │              │               │                │
│         └──────────────┼───────────────┘                │
│                        │                                │
│  ┌──────────────────────────────────┐                   │
│  │       app/services/ (Orchestration)                 │
│  │  ┌─────────────────┐  ┌──────────────┐              │
│  │  │ separation_     │  │ playback_    │              │
│  │  │ service.py      │  │ service.py   │              │
│  │  └─────────────────┘  └──────────────┘              │
│  │  ┌─────────────────┐  ┌──────────────┐              │
│  │  │ export_service  │  │ settings_    │              │
│  │  │ .py             │  │ controller   │              │
│  │  └─────────────────┘  └──────────────┘              │
│  └──────────────────────────────────┘                   │
└────────────────────────┬───────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────┐
│                    engine/ (Processing)                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐         │
│  │  audio/    │  │ inference/ │  │  export/   │         │
│  └────────────┘  └────────────┘  └────────────┘         │
│         │              │               │                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐         │
│  │  demucs/   │  │  weights/  │  │  errors/   │         │
│  └────────────┘  └────────────┘  └────────────┘         │
│         │              │               │                │
│  ┌──────────────────────────────────┐                   │
│  │       engine/performance/        │                   │
│  │  ┌────────────┐  ┌────────────┐  │                   │
│  │  │ profiler   │  │ monitor    │  │                   │
│  │  └────────────┘  └────────────┘  │                   │
│  └──────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

## Module Dependencies

### app/ Layer

```
app/ui/main_window.py
  → app/controllers/main_controller.py
  → app/controllers/settings_controller.py
  → app/controllers/playback_controller.py
  → app/widgets/* (all widgets)
  → app/models/app_state.py
  → app/models/settings_model.py
  → app/services/separation_service.py
  → app/services/playback_service.py
  → app/services/export_service.py

app/controllers/main_controller.py
  → app/services/separation_service.py
  → app/services/export_service.py
  → app/models/app_state.py
  → app/models/settings_model.py
  → app/workers/audio_load_worker.py
  → app/workers/separation_worker.py

app/controllers/playback_controller.py
  → app/services/playback_service.py
  → app/models/app_state.py

app/controllers/settings_controller.py
  → app/models/settings_model.py

app/widgets/waveform_view.py
  → app/widgets/progress_bar.py
  → app/audio/audio_mixer.py

app/widgets/playback_controls.py
  → app/widgets/progress_bar.py

app/widgets/track_selector.py
  → app/widgets/progress_bar.py
```

### app/services/ Layer (Orchestration)

```
app/services/separation_service.py
  → engine/audio/loader.py (AudioLoader)
  → engine/inference/pipeline.py (InferencePipeline)
  → engine/demucs/separator.py (DemucsSeparator)
  → engine/performance/monitor.py (ResourceMonitor)
  → app/models/app_state.py

app/services/playback_service.py
  → app/audio/audio_mixer.py (AudioMixer)
  → app/models/app_state.py

app/services/export_service.py
  → engine/export/writer.py (ExportWriter)
  → engine/export/batch_exporter.py (BatchExporter)
  → engine/export/config.py (ExportConfig)
```

### engine/ Layer

```
engine/demucs/separator.py
  → engine/inference/pipeline.py (InferencePipeline)
  → engine/audio/preprocessor.py (AudioPreprocessor)
  → engine/audio/postprocessor.py (AudioPostprocessor)
  → engine/demucs/config.py
  → engine/demucs/errors.py

engine/inference/pipeline.py
  → engine/inference/model_manager.py (ModelManager)
  → engine/inference/config.py
  → engine/inference/errors.py

engine/inference/model_manager.py
  → engine/inference/demucs_agent.py (DemucsAgent)
  → engine/inference/openunmix_agent.py (OpenUnmixAgent)
  → engine/inference/config.py

engine/inference/demucs_agent.py
  → demucs.api (external)
  → torch (external)

engine/inference/openunmix_agent.py
  → openunmix (external)
  → torch (external)

engine/audio/loader.py
  → librosa (external)
  → soundfile (external)
  → audioread (external)
  → engine/audio/resampler.py
  → engine/audio/errors.py

engine/audio/resampler.py
  → resampy (external)
  → engine/audio/errors.py

engine/audio/preprocessor.py
  → numpy (external)
  → engine/audio/errors.py

engine/audio/postprocessor.py
  → numpy (external)
  → engine/audio/errors.py

engine/audio/metadata.py
  → mutagen (external)
  → soundfile (external)

engine/export/writer.py
  → soundfile (external)
  → mutagen (external)
  → engine/export/config.py
  → engine/export/errors.py

engine/export/batch_exporter.py
  → engine/export/writer.py (ExportWriter)
  → engine/export/config.py

engine/export/metadata.py
  → mutagen (external)
  → engine/export/errors.py

engine/performance/monitor.py
  → psutil (external)

engine/performance/profiler.py
  → cProfile (stdlib)
  → torch.profiler (external)
```

## External Dependencies

### Core Dependencies

| Package | Used By | Purpose |
|---------|---------|---------|
| `torch` | inference/demucs_agent, inference/openunmix_agent | ML backend |
| `torchaudio` | inference/demucs_agent | Audio tensor operations |
| `demucs` | inference/demucs_agent | Demucs separation model |
| `openunmix` | inference/openunmix_agent | Open-Unmix separation model |
| `librosa` | audio/loader | Audio file loading |
| `soundfile` | audio/loader, audio/metadata, export/writer | WAV/FLAC reading/writing |
| `audioread` | audio/loader | Audio format decoding |
| `resampy` | audio/resampler | Audio resampling |
| `numpy` | audio/*, inference/*, export/* | Numerical computing |
| `scipy` | audio/preprocessor, audio/postprocessor | Signal processing |
| `mutagen` | audio/metadata, export/metadata | Metadata reading/writing |
| `PySide6` | app/ui, app/widgets, app/controllers | GUI framework |
| `pyqtgraph` | app/widgets/waveform_view | Waveform visualization |
| `aiofiles` | app/services/* | Async file I/O |
| `pydantic` | app/models/*, engine/inference/config, engine/export/config | Data models |
| `loguru` | all modules | Logging |
| `psutil` | engine/performance/monitor | System resource monitoring |

### Dev Dependencies

| Package | Purpose |
|---------|---------|
| `pytest` | Test framework |
| `pytest-asyncio` | Async test support |
| `pytest-qt` | Qt UI testing |
| `pytest-cov` | Coverage reporting |
| `pytest-benchmark` | Performance benchmarking |
| `ruff` | Linting and formatting |
| `mypy` | Type checking |
| `pre-commit` | Git hooks |
| `pyinstaller` | Packaging |
| `memory-profiler` | Memory profiling |
| `py-spy` | CPU profiling |
| `snakeviz` | Profile visualization |
