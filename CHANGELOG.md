# Changelog

All notable changes to Descombinator Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Phase 8: Performance Optimization — profiling infrastructure (`cProfile`, `py-spy`, `memory_profiler`, `torch.profiler`), `engine/performance/` package with `ResourceMonitor` and `TorchRuntimeOptimizer`, benchmark suite with 16 gates, CI regression job
- Phase 8: Lazy imports (PEP 562) for startup optimization — `import main` loads none of the ML stack
- Phase 8: WAV-PCM `np.memmap` fast path for large file loading
- Phase 8: `separate_loaded()` method on `SeparationService` to avoid double audio decode
- Phase 8: Worker-side waveform decimation for UI responsiveness
- Phase 8: Guarded CUDA support (`torch.cuda.amp.autocast()`, pinned memory, segment/jobs config)
- Phase 8: `scripts/profiling/` directory with `profile_cpu.py`, `profile_memory.py`, `profile_torch.py`, `profile_pyspy.py`, `measure_startup.py`
- Phase 8: `benchmarks/` package with `baselines.json` and `scripts/bench/check_regressions.py`
- Phase 7: `AudioMixer` in `app/audio/` — in-memory mixer with `QAudioSink` for synchronized gapless multi-track playback
- Phase 7: `PlaybackStateStore` — persists volumes, mutes, active stems, and last file
- Phase 7: `TrackMixerWidget` — per-track volume sliders and mute toggles
- Phase 7: Seek slider with live drag seeking and `m:ss` time display
- Phase 6: `ProcessingDialog` — modal progress dialog with cancel button and ETA calculation
- Phase 6: `SettingsDialog` — settings UI with model/format/sample-rate/bitrate/theme controls
- Phase 6: `AudioLoadWorker` — `QRunnable` for background audio loading
- Phase 5: Multi-format export (WAV, FLAC, MP3, M4A) with metadata embedding
- Phase 5: `BatchExporter` with progress tracking and error handling
- Phase 4: `InferenceError` added to `engine/demucs/errors.py` exception hierarchy
- Phase 4: State machine for separation workflow (idle → loading → processing → complete → error)
- Phase 3: `ModelManager` with `SeparationModel` protocol, cache, and lazy factory
- Phase 3: `torch.inference_mode()` applied in both `DemucsAgent` and `OpenUnmixAgent`
- Phase 2: `MetadataReader` and `MetadataWriter` via `mutagen`
- Phase 2: `AudioPostprocessor` with artifact reduction (windowing, crossfading, peak limiting)
- Phase 1: Pre-commit hooks (ruff, ruff-format, trailing-whitespace, end-of-file, check-yaml, check-toml, check-merge-conflict, large-files)
- Phase 1: GitHub Actions CI workflow with lint, format, test, mypy, and benchmark jobs
- Phase 1: `docs/` structure (architecture, guides, development, troubleshooting)
- Phase 1: `assets/` structure (icons, styles, i18n)

### Changed

- `requirements.txt`: Updated all minimum version specifiers to match latest installed versions
- `requirements-dev.txt`: Updated all minimum version specifiers to match latest versions
- `AGENTS.md`: Added Phase Status table and expanded Skills list
- `readme.md`: Updated Project Status, Tech Stack, Features, Installation, Development, and Roadmap sections
- `roadmap.md`: Added Current Status summary
- `main.py`: Rewritten as `QApplication` entry point with controller creation and `MainWindow` display
- `MainController`: Added `separation_progress` signal, fixed `SeparationService()` to `SeparationService(SeparationConfig())`
- `PlaybackController`: Removed `asyncio.create_task()` call; `PlaybackService.load_file()` made synchronous
- `SettingsController`: Added `self._settings = SettingsModel()` initialization in `__init__`
- `MainWindow`: Removed `initialize_services()` call, added "Separate" button and Settings menu item, wired `ProcessingDialog` to separation signals
- `ProgressBar`: Added `set_error()` method with red styling
- `MetadataReader.read()`: Wraps `sf.info()` in `asyncio.to_thread()` for async-first consistency
- `MetadataWriter`: Uses ID3 Frame objects (`TIT2`, `TPE1`, `TALB`) via `mutagen.id3` for WAV/AIFF
- `ModelName` and `DeviceType`: Changed from `str, Enum` to `StrEnum` (Python 3.11+)
- `InferencePipeline`: Removed unused `_resampler` attribute
- `model_manager.py`: Removed unused `ModelLoadError` import, added `try/except ValueError` for clean `ModelNotFoundError`
- CI: Added `concurrency` group, `permissions: contents: read`, `fail-fast: false`
- CI: Added pip caching via `actions/setup-python@v5` cache
- CI: Added `libegl1 libgl1 libopengl0 libpulse0 ffmpeg` system dependencies
- CI: Added `xvfb` for UI tests
- CI: Set coverage thresholds: unit/integration `--cov-fail-under=60`, UI `--cov-fail-under=40`
- CI: Added `QT_QPA_PLATFORM=offscreen` for unit/integration tests
- CI: Added `benchmark` job with regression gate (`scripts/bench.check_regressions.py`)
- CI: Added Codecov upload and coverage artifact upload
- `pyproject.toml`: Added `pydantic>=2.0.0` to dependencies, added mypy overrides for Phase 6/7 drift

### Fixed

- `build-backend` in `pyproject.toml`: Changed from deprecated `setuptools.backends._legacy:_Backend` to `setuptools.build_meta`
- Pre-commit ruff version: Updated from `v0.5.0` to `v0.16.1`
- Pre-commit-hooks: Updated from `v4.6.0` to `v5.0.0` (fixes deprecated stage names)
- Pre-commit: Added `check-merge-conflict` and `check-toml` hooks
- CI: Fixed malformed `setup-python` action reference (dot → slash)
- CI: Corrected OpenGL package names for Ubuntu 24.04
- CI: Added `libpulse0` and `ffmpeg` to benchmark job
- CI: Set realistic coverage thresholds for unit and UI tests
- CI: Added `QT_QPA_PLATFORM=offscreen` for UI tests and benchmark
- CI: Run regression check as module to fix import path
- `tests/conftest.py`: Removed redundant marker definitions (already in `pyproject.toml`)
- `scripts/profiling/profile_memory.py`: Fixed psutil-based RSS sampling, mock pipeline init
- `scripts/profiling/_mem_runner.py`: Fixed mock initialization
- Pre-existing integration drift: Repaired and cleaned mypy config
- Pre-existing ruff drift: Resolved and fixed drop-event accept bug

### Removed

- `QMediaPlayer`/`QAudioOutput` from `PlaybackService` (replaced with in-memory `AudioMixer` + `QAudioSink`)
- `initialize_services()` method from `MainController` (redundant with lazy init)
- `asyncio.create_task()` call from `PlaybackController` (synchronous `load_file()`)
- Unused `_resampler` from `InferencePipeline`
- Unused `ModelLoadError` import from `model_manager.py`

## [0.1.0] — 2026-08-02

Initial release with core audio separation functionality.

### Added

- Phase 1: Project Foundation — virtual environment, dependencies, CI scaffolding, project structure
- Phase 2: Audio I/O & DSP Pipeline — `AudioLoader`, `AudioResampler`, `AudioPreprocessor`, `AudioPostprocessor`, `MetadataReader`, `MetadataWriter`
- Phase 3: ML Model Integration & Inference — `DemucsAgent`, `OpenUnmixAgent`, `InferencePipeline`, `ModelManager`
- Phase 4: Separation Engine Core — `DemucsSeparator`, `SeparationService`, state machine, progress reporting
- Phase 5: Export Pipeline — `ExportWriter`, `BatchExporter`, `ExportConfig`, metadata embedding
- Phase 6: PySide6 UI Development — `MainWindow`, `FileDropZone`, `PlaybackControls`, `WaveformView`, `TrackSelector`, `ProgressBar`, controllers, models, services
- Phase 7: Media Playback & Visualization — `AudioMixer`, `PlaybackController`, `PlaybackStateStore`, `TrackMixerWidget`, seek slider, time display
- Phase 8: Performance Optimization — profiling, monitoring, optimization, benchmarks, CI regression gate

### Known Issues

- GPU acceleration requires CUDA 12+ and is guarded by `torch.cuda.is_available()`
- Coverage gates (Phase 9) are in progress — current thresholds are baselined at 60% (unit/integration) and 40% (UI)
- Packaging and distribution (Phase 10) not yet implemented
- Documentation site (Phase 11) not yet generated
