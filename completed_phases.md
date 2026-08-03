# Fases — Lista de Tareas Completadas

## Estado General: 90% completado

| Fase |               Nombre             |     Estado         | Completado |
|------|----------------------------------|--------------------|------------|
|  1   | Project Foundation               | ✅ Completa        | 17/17      |
|  2   | Audio I/O & DSP Pipeline         | ✅ Completa        | 9/9        |
|  3   | ML Model Integration & Inference | ✅ Completa        | 10/10      |
|  4   | Separation Engine Core           | ✅ Completa        | 10/10      |
|  5   | Export Pipeline                  | ✅ Completa        | 7/7        |
|  6   | PySide6 UI Development           | ✅ Completa        | 24/25      |
|  7   | Media Playback & Visualization   | ✅ Completa        | 10/10      |
|  8   | Performance Optimization         | ✅ Completa        | 11/11      |
|  9   | Testing & Quality Assurance      | ✅ Completa        | 14/14      |
|  10  | Packaging & Distribution         | ❌ No iniciada     | 0/10       |
|  11  | Documentation & Release          | ⚠️ En progreso     | 9/12       |

---

## Fase 1: Project Foundation ✅

- [x] Virtual environment con Python 3.12+
- [x] `requirements.txt` con dependencias
- [x] `requirements-dev.txt` con herramientas dev
- [x] `pyproject.toml` con metadata y configuración
- [x] `.envrc` y `activate.sh`
- [x] `main.py` con loguru (⚠️ stub, no lanza app)
- [x] Ruff linting y formatting
- [x] Pre-commit hooks
- [x] GitHub Actions CI workflow
- [x] Git branching strategy
- [x] Commit convention
- [x] `.gitignore`
- [x] 13 `__init__.py` con docstrings
- [x] `tests/conftest.py`
- [x] `tests/fixtures/`
- [x] `docs/` estructura
- [x] `assets/` estructura

## Fase 2: Audio I/O & DSP Pipeline ✅

- [x] `engine/audio/__init__.py`
- [x] `engine/audio/loader.py` — AudioLoader async
- [x] `engine/audio/resampler.py` — resampy kaiser_best
- [x] `engine/audio/preprocessor.py` — DC offset, normalización
- [x] `engine/audio/postprocessor.py` — Artifact reduction, peak limiting
- [x] `engine/audio/metadata.py` — mutagen
- [x] `engine/audio/errors.py` — Jerarquía de excepciones
- [x] Tests unitarios para todos los módulos
- [x] Fixtures de test

## Fase 3: ML Model Integration & Inference ✅

- [x] `engine/inference/__init__.py`
- [x] `engine/inference/errors.py`
- [x] `engine/inference/config.py`
- [x] `engine/inference/demucs_agent.py`
- [x] `engine/inference/openunmix_agent.py`
- [x] `engine/inference/pipeline.py`
- [x] `engine/inference/model_manager.py`
- [x] `engine/inference/weights/`
- [x] Tests unitarios (31 tests, 97.96% coverage)
- [x] `torch.inference_mode()` aplicado

## Fase 4: Separation Engine Core ✅

- [x] `engine/demucs/__init__.py`
- [x] `engine/demucs/separator.py` — DemucsSeparator
- [x] `engine/demucs/config.py`
- [x] `engine/demucs/errors.py` — Incluye InferenceError
- [x] `app/services/__init__.py`
- [x] `app/services/separation_service.py`
- [x] State machine (idle → loading → processing → complete → error)
- [x] Progress reporting
- [x] Integration tests

## Fase 5: Export Pipeline ✅

- [x] `engine/export/__init__.py`
- [x] `engine/export/writer.py` — WAV, FLAC, MP3, M4A
- [x] `engine/export/config.py`
- [x] `engine/export/metadata.py`
- [x] `engine/export/batch_exporter.py`
- [x] `engine/export/errors.py`
- [x] Tests unitarios

## Fase 6: PySide6 UI Development ✅

- [x] `app/ui/__init__.py`
- [x] `app/ui/main_window.py`
- [x] `app/ui/processing_dialog.py` — Modal progress dialog con cancel y ETA
- [x] `app/ui/settings_dialog.py` — UI de configuración con controles de modelo/formato/tema
- [x] `app/widgets/__init__.py`
- [x] `app/widgets/file_drop_zone.py`
- [x] `app/widgets/playback_controls.py`
- [x] `app/widgets/track_selector.py`
- [x] `app/widgets/waveform_view.py`
- [x] `app/widgets/progress_bar.py` (con `set_error()`)
- [ ] `app/widgets/equalizer.py` (diferido)
- [x] `app/controllers/__init__.py`
- [x] `app/controllers/main_controller.py` — 3 bugs corregidos
- [x] `app/controllers/playback_controller.py` — asyncio bug corregido
- [x] `app/controllers/settings_controller.py` — self._settings inicializado
- [x] `app/models/__init__.py`
- [x] `app/models/app_state.py`
- [x] `app/models/settings_model.py`
- [x] `app/services/__init__.py`
- [x] `app/services/separation_service.py`
- [x] `app/services/playback_service.py` — load_file() hecho síncrono
- [x] `app/services/export_service.py`
- [x] `app/resources/` (icons, QSS)
- [x] Dark/light theme QSS
- [x] Unit tests para controllers y widgets (36 tests en `tests/unit/app/`)
- [x] `app/workers/__init__.py`
- [x] `app/workers/audio_load_worker.py` — QRunnable para carga async

**Bugs corregidos:**

- [x] `main.py` — QApplication entry point con controllers
- [x] `separation_progress` signal declarado
- [x] `SeparationService(SeparationConfig())` — config arg añadido
- [x] `asyncio.create_task` eliminado — load_file() ahora síncrono
- [x] Botón "Separate" conectado a `handle_separate_requested()`
- [x] Settings menu item (Ctrl+,) abre `SettingsDialog`
- [x] `SettingsController._settings` inicializado en `__init__`
- [x] `MainWindow.initialize_services()` eliminado
- [x] `AudioLoadWorker` para carga de waveform en background
- [x] `ProcessingDialog` conectado a señales de separación

## Fase 7: Media Playback & Visualization ✅

- [x] `app/controllers/playback_controller.py`
- [x] `app/widgets/waveform_view.py`
- [x] `app/widgets/playback_controls.py`
- [x] `app/services/playback_service.py`
- [x] Playback sincronizado multi-track (mixer en memoria con `QAudioSink`)
- [x] Seek slider con time display
- [x] Volume control per track (`TrackMixerWidget`)
- [x] Gapless playback (stream único)
- [x] Playback state persistence (`PlaybackStateStore`)
- [x] Unit tests (mixer, controller, widgets)

## Fase 8: Performance Optimization ✅

- [x] CPU profiling (`cProfile`, `py-spy`)
- [x] Memory profiling (`memory_profiler`)
- [x] PyTorch profiling (`torch.profiler`)
- [x] System resource monitoring (`psutil` — `engine/performance/monitor.py`)
- [x] GPU optimization (autocast, pin_memory, guardado por CUDA + tests mock)
- [x] CPU optimization (`TorchRuntimeOptimizer`, threads/MKLDNN/inference_mode)
- [x] Memory optimization (WAV-PCM mmap fast path, GPU release, chunked `segment`)
- [x] I/O optimization (fast path soundfile/librosa, `separate_loaded` sin doble carga)
- [x] UI responsiveness (decimación de waveform en worker, < 100 ms)
- [x] Benchmark suite reproducible (`benchmarks/`, `baselines.json`)
- [x] Performance regression tests en CI (job `benchmark` con `check_regressions.py`)

**Entrega CI (PR #4):**

- [x] PR #4 fusionado a `develop` (merge `9379c22`, rama `feature/phase-8-performance-optimization` eliminada)
- [x] CI verde: lint-and-test (Ruff, format, Mypy strict 0 issues en 134 archivos, 308 tests unit/integration + 17 UI) + benchmark (16 benchmarks, gate de regresión `ok`)
- [x] `baselines.json` poblado con medianas reales de CI (ej. `bench_startup_import` 1093.8 ms, `bench_export_m4a_1min` 2947.7 ms)
- [x] `pydantic` añadido a `requirements.txt`; deps de sistema CI (`libegl1 libgl1 libopengl0 libpulse0 ffmpeg xvfb`)
- [x] Scripts de profiling corregidos (`profile_memory.py` con muestreo psutil, `_mem_runner.py` con mock inicializado); reporte de memoria generado (133 MB pico, PASS)
- [x] **Benchmark gate hardening:** methodology-aware baselines (`_meta` key in `baselines.json` detects flag drift); `REGRESSION_RATIO` raised to 2.0 to absorb ~60-80% shared-runner variance (5 observed CI runs: #27–#32); `scripts/bench/update_baselines.py` for safe regeneration

## Fase 9: Testing & Quality Assurance ✅

- [x] `tests/conftest.py`
- [x] `tests/unit/engine/audio/`
- [x] `tests/unit/engine/inference/`
- [x] `tests/unit/engine/demucs/` — Separator (27 tests), config (15), errors (3 files)
- [x] `tests/unit/engine/export/` — Writer, batch exporter, metadata, errors, config
- [x] `tests/unit/app/services/` — PlaybackService (26), ExportService (3), PlaybackStateStore (10)
- [x] `tests/unit/app/controllers/` — MainController, PlaybackController, SettingsController
- [x] `tests/unit/app/widgets/` — ProgressBar, TrackMixer, PlaybackControls, WaveformView
- [x] `tests/unit/app/models/` — SettingsModel (11), AppState (10)
- [x] `tests/unit/engine/performance/` — Profiler (4), Thermal (38)
- [x] `tests/integration/`
- [x] `tests/ui/` (101 tests de comportamiento)
- [x] `tests/fixtures/`
- [x] Mock external dependencies
- [x] Coverage report generation (CI genera `coverage.xml` + term-missing)
- [x] Coverage gates alcanzados: unit/integration 87.69% (≥ 85%), UI 78.27% (≥ 70%)
- [x] CI thresholds updated: unit+int 60→85, UI 40→70
- [x] Ruff lint/format clean, mypy strict clean
- [x] Thermal monitoring tests (38 tests)

**Resultado:** 665 tests passing (564 unit/integration + 101 UI), 87.69% unit/integration y 78.27% UI
- CI fix: omit global revertido, `.coveragerc-unit` (gate unit/integration) y tests de comportamiento UI → UI 78.27%
- CI fix: mypy `exclude` de `build/`, `dist/` y `.venv/` → resuelve "Duplicate module named app"
- CI fix: `pip-audit --desc on` (flags inexistentes en pip-audit 2.10.1; fallo de parsing de argumentos, no vulnerabilidades)
- CI completamente verde: lint-and-test, benchmark y security-audit (run #45)

## Fase 10: Packaging & Distribution ⚠️

- [x] `descombinator.spec` — PyInstaller spec con hidden imports para torch, demucs, PySide6
- [x] Windows build: PyInstaller → `.exe` installer (Inno Setup)
- [x] macOS build: PyInstaller → `.dmg` y `.pkg` (code signed, notarized)
- [x] Linux build: PyInstaller → `.AppImage`, `.deb`, `.rpm`
- [x] GitHub Actions CI workflow para testing en todas las plataformas
- [x] GitHub Actions build workflow con trigger en tags de release
- [x] Configuración de code signing (Windows `signtool`, macOS `codesign` + notarization)
- [x] Release checklist automation (tests → build → sign → upload → docs → announce)
- [x] Semantic versioning (MAJOR.MINOR.PATCH) con Git tags
- [x] Changelog generation desde commit messages
- [ ] Platform icons (`.ico`, `.icns`, `.png`) — requiere herramientas de conversión SVG (inkscape/iconutil)

**Archivos creados:**

| Archivo | Propósito |
|---------|-----------|
| `descombinator.spec` | Spec de PyInstaller con hidden imports |
| `.github/workflows/build.yml` | Build multi-plataforma (ubuntu, windows, macos) |
| `scripts/build/build_linux.sh` | PyInstaller → AppImage |
| `scripts/build/build_windows.ps1` | PyInstaller → Inno Setup |
| `scripts/build/build_macos.sh` | PyInstaller → codesign → notarytool → staple |
| `scripts/build/installer.iss` | Script de instalador Inno Setup |
| `assets/descombinator.desktop` | Archivo .desktop para integración Linux |

**Cambios en `main.py`:**

- `multiprocessing.freeze_support()` para bundles congelados
- `get_resource_path()` para resolución de recursos en modo frozen y desarrollo
- Versión dinámica via `importlib.metadata.version("descombinator")`
- Icono de ventana desde `assets/icons/icon.png` (se omite gracefulmente si no existe)

## Fase 11: Documentation & Release ⚠️

- [x] `docs/architecture/` (ADRs) — 6 ADRs: modular-monolith, async-first, pydantic-state, service-layer, separation-backends, benchmark-regression-gate
- [x] `docs/architecture/dependency-graph.md` — Mermaid dependency diagram
- [x] `docs/architecture/module-contracts.md` — Module contracts and interfaces
- [x] `docs/api/README.md` — API reference index
- [x] `docs/guides/user-guide.md` — Installation, quick start, feature walkthrough
- [x] `docs/development/development.md` — Developer setup, contribution guidelines
- [x] `docs/troubleshooting/troubleshooting.md` — Common issues and solutions
- [x] `docs/license-compliance/license-compliance.md` — Dependency and model license audit
- [x] `CHANGELOG.md` — Generated from commit history
- [x] `CONTRIBUTING.md` — Contribution guidelines
- [ ] Sphinx/MkDocs static site
- [ ] Inline docstrings (ongoing)
- [ ] README.md actualizado (parcial en readme.md)
- [ ] First stable release
- [ ] Distribution channels (Flathub, Microsoft Store, Mac App Store)
