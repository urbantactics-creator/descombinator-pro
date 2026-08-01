# Descombinator Pro — Roadmap

> **Phase-by-phase plan** to build the complete on-device audio separation desktop application, from foundation to distributable release.

---

## Overview

| Phase | Name | Duration (est.) | Dependencies |
| ------- | ------ | ----------------- | -------------- |
| 1 | Project Foundation | Sprint 1 | — |
| 2 | Audio I/O & DSP Pipeline | Sprint 2 | Phase 1 |
| 3 | ML Model Integration & Inference | Sprint 3–4 | Phase 2 |
| 4 | Separation Engine Core | Sprint 4–5 | Phase 3 |
| 5 | Export Pipeline | Sprint 5–6 | Phase 4 |
| 6 | PySide6 UI Development | Sprint 6–8 | Phase 1 |
| 7 | Media Playback & Visualization | Sprint 8 | Phase 6 |
| 8 | Performance Optimization | Sprint 9 | Phases 2–7 |
| 9 | Testing & Quality Assurance | Sprint 10 | Phases 1–8 |
| 10 | Packaging & Distribution | Sprint 11 | Phase 9 |
| 11 | Documentation & Release | Sprint 12 | Phase 10 |

---

## Phase 1: Project Foundation

**Goal:** Establish the development environment, coding standards, CI scaffolding, and project structure so the team can start building features on a solid base.

### Deliverables

- [x] Virtual environment with Python 3.12+ and all dependencies installed
- [x] `requirements.txt` with pinned dependencies
- [x] `requirements-dev.txt` with dev tools (ruff, mypy, pytest, pre-commit)
- [x] `pyproject.toml` with project metadata, build config, and tool configuration (ruff, mypy, pytest, coverage)
- [x] `.envrc` and `activate.sh` for environment auto-activation
- [x] `main.py` async entry point with loguru configuration
- [x] Ruff linting (`ruff check`) and formatting (`ruff format`) configuration
- [x] Pre-commit hooks (ruff, ruff-format, trailing-whitespace, end-of-file, check-yaml, check-toml, check-merge-conflict, large-files)
- [x] GitHub Actions CI workflow (lint, format, test, mypy with `continue-on-error`)
- [x] Git branching strategy: `master` + `develop` branches created and pushed
- [x] Commit convention enforced (`type(scope): subject`)
- [x] `.gitignore` with venv, cache, build artifacts, logs, coverage, env files
- [x] 13 `__init__.py` files with module-level docstrings
- [x] `tests/conftest.py` with shared fixtures and markers
- [x] `tests/fixtures/` directory for test data
- [x] `docs/` structure (architecture, guides, development, troubleshooting)
- [x] `assets/` structure (icons, styles, i18n)

### Skills Applied

- `python-backend-engineer` — Coding standards, async patterns, type hints
- `devops-engineer` — CI/CD scaffolding, environment configuration
- `project-architect` — Module boundaries, dependency graph

### Key Decisions

- **Architecture:** Modular monolith with clear `app/` ↔ `engine/` layer separation
- **State management:** Pydantic models + `enum.Enum` for FSM state machines
- **Logging:** `loguru` exclusively, no `logging.basicConfig()`
- **Async-first:** All I/O operations use `async def`
- **Build backend:** `setuptools.build_meta` (modern, not legacy)
- **CI strictness:** mypy strict mode enabled from day one, CI runs with `continue-on-error` until Phase 2 adds typed code
- **Pre-commit:** ruff (lint + format) + standard hooks, no mypy hook (too noisy on empty packages)

### Phase 1 Fixes (Review)

- Fixed `build-backend` from deprecated `setuptools.backends._legacy:_Backend` to `setuptools.build_meta`
- Updated pre-commit ruff version from `v0.5.0` to `v0.16.1` (matches installed version)
- Updated pre-commit-hooks from `v4.6.0` to `v5.0.0` (fixes deprecated stage names)
- Added `check-merge-conflict` and `check-toml` hooks
- Added CI `concurrency` group to cancel in-progress runs
- Added CI `permissions: contents: read` for security
- Added CI `fail-fast: false` so all matrix jobs run
- Added CI pip caching via `actions/setup-python@v5` cache
- Removed redundant marker definitions from `conftest.py` (already in `pyproject.toml`)

---

## Phase 2: Audio I/O & DSP Pipeline

**Goal:** Implement the audio loading, resampling, format conversion, and preprocessing capabilities in `engine/audio/`.

### Deliverables

- [x] `engine/audio/__init__.py` — Public API exports
- [x] `engine/audio/loader.py` — `AudioLoader` class with async `load()` supporting MP3, WAV, FLAC, M4A, OGG
- [x] `engine/audio/resampler.py` — Resampling using `resampy` with `kaiser_best` quality, target 44.1 kHz
- [x] `engine/audio/preprocessor.py` — DC offset removal, peak normalization to -1 dBFS
- [x] `engine/audio/postprocessor.py` — Artifact reduction (windowing, crossfading), peak limiting
- [x] `engine/audio/metadata.py` — Metadata reading/writing via `mutagen`
- [x] `engine/audio/errors.py` — Audio-specific exception hierarchy
- [x] Unit tests for all audio I/O modules (`tests/unit/engine/audio/`)
- [x] Test fixtures in `tests/fixtures/` (synthetic WAV files < 1 MB)

### Skills Applied

- `audio-dsp-engineer` — DSP pipeline design, format handling, preprocessing/postprocessing
- `python-backend-engineer` — Async I/O with `asyncio.to_thread`, type hints, error handling
- `code-reviewer` — Code review, best practices validation

### Key Patterns

```python
# AudioLoader interface
class AudioLoader:
    async def load(self, path: Path, sr: int = 44100, mono: bool = True) -> np.ndarray: ...
    def validate_exists(self, path: Path) -> None: ...
    def validate_format(self, path: Path) -> None: ...
```

### Quality Targets

- Support all major audio formats (MP3, WAV, FLAC, M4A, OGG)
- Resample to 44.1 kHz (Demucs native) with high-quality `kaiser_best`
- Preserve original metadata on export

### Phase 2 Review Notes

**Deviations from plan:**

- **Resampling filter:** Used `kaiser_best` instead of `sinc_best` — resampy 0.4.3 does not include `sinc_best` filter data. `kaiser_best` is the highest quality filter available.
- **`bit_depth` type:** Changed from `int | None` to `str | None` — `soundfile.info().subtype_info` returns descriptive strings (e.g., "Signed 16 bit PCM"), not integers.
- **Metadata reading:** `MetadataReader.read()` wraps `sf.info()` in `asyncio.to_thread()` for async-first consistency, even though it's a fast header read.
- **Metadata writing:** WAV/AIFF files use ID3 Frame objects (`TIT2`, `TPE1`, `TALB`) via `mutagen.id3` instead of `easy=True` dict-style tags, which don't work for WAV.
- **Coverage:** Achieved 91.43% (target ≥90%). `loader.py` at 89% and `metadata.py` at 86% are below 90% individually but overall meets target.

**Test results:** 53/53 passed, ruff clean, all 15 public API exports verified.

---

## Phase 3: ML Model Integration & Inference

**Goal:** Integrate Demucs and Open-Unmix models, build the inference pipeline in `engine/inference/`, and implement model lifecycle management.

### Deliverables

- [x] `engine/inference/__init__.py` — Public API exports (12 symbols)
- [x] `engine/inference/errors.py` — Inference-specific exception hierarchy
- [x] `engine/inference/config.py` — `InferenceConfig` Pydantic model with `ModelName`/`DeviceType` enums
- [x] `engine/inference/demucs_agent.py` — `DemucsAgent` wrapping `demucs.api.Separator` with lazy init
- [x] `engine/inference/openunmix_agent.py` — `OpenUnmixAgent` wrapping `openunmix.predict` with batch dim squeeze
- [x] `engine/inference/pipeline.py` — `InferencePipeline` orchestrating preprocess → inference → numpy output
- [x] `engine/inference/model_manager.py` — `ModelManager` with `SeparationModel` protocol, cache, lazy factory
- [x] `engine/inference/weights/` — Directory for cached model weights
- [x] Unit tests for all inference modules (`tests/unit/engine/inference/` — 31 tests, 97.96% coverage)
- [x] `torch.inference_mode()` applied in both agents' `separate()` methods

### Intentionally Deferred

- **Model integrity verification (SHA-256)** — Defer to Phase 4 when export pipeline exists
- **HuggingFace `huggingface_hub` integration** — Both libraries handle downloads internally
- **GPU support (`torch.cuda.amp.autocast()`)** — No CUDA available; `DeviceType.CUDA` enum ready for future
- **CPU optimization (`torch.set_num_threads()`, `torch.backends.mkldnn`)** — Defer to Phase 8

### Skills Applied

- `ai-ml-engineer` — Model integration, PyTorch optimization, inference pipeline design
- `model-manager` — Model lifecycle, caching, switching
- `audio-separation-specialist` — Model selection, quality evaluation
- `python-backend-engineer` — Async patterns, error handling
- `code-reviewer` — Code review, best practices validation

### Key Patterns

```python
# SeparationModel Protocol — both agents satisfy this interface
class SeparationModel(Protocol):
    async def initialize(self) -> None: ...
    async def separate(self, audio: torch.Tensor) -> dict[str, torch.Tensor]: ...
    @property
    def sources(self) -> list[str]: ...

# Lazy model creation in ModelManager._create_model()
def _create_model(self, name: str) -> SeparationModel:
    if name in (ModelName.HTDEMUCS_FT.value, ModelName.MDX_EXTRA.value):
        from engine.inference.demucs_agent import DemucsAgent
        return DemucsAgent(config)
    elif name == ModelName.UMXHQ.value:
        from engine.inference.openunmix_agent import OpenUnmixAgent
        return OpenUnmixAgent(config)
```

### Model Stack

| Model | Purpose | Backend | Agent |
| --- | --- | --- | --- |
| `htdemucs_ft` | Primary separation | PyTorch/Demucs | `DemucsAgent` |
| `mdx_extra` | High-quality alternative | PyTorch/Demucs | `DemucsAgent` |
| `umxhq` | Secondary/alternative | PyTorch/OpenUnmix | `OpenUnmixAgent` |

### Phase 3 Review Notes

**Deviations from plan:**

- **`StrEnum` instead of `str, Enum`:** Ruff flagged `class ModelName(str, Enum)` as UP042. Changed to `StrEnum` (Python 3.11+) which is equivalent but cleaner.
- **Removed unused `_resampler` from `InferencePipeline`:** Pipeline creates `AudioResampler` but never uses it — removed dead code.
- **Removed unused `ModelLoadError` import from `model_manager.py`:** Was imported but never referenced.
- **Added `torch.inference_mode()` in agents:** Plan noted `torch.inference_mode()` is preferred over `torch.no_grad()`. Added to both `DemucsAgent.separate()` and `OpenUnmixAgent.separate()` for inference optimization.
- **`_create_model()` ValueError handling:** `ModelName("bogus")` raises `ValueError` before reaching the `else` branch. Added explicit `try/except ValueError` to raise `ModelNotFoundError` cleanly.

**Plan items confirmed correct:**

- Demucs `separate_tensor()` returns `(original_tensor, stems_dict)` — destructured correctly.
- OpenUnmix output has extra batch dim `(1, C, T)` — squeezed correctly.
- Both agents use `asyncio.to_thread()` for CPU-bound operations — correct.
- `ModelManager._create_model()` uses lazy imports — correct.
- `SeparationModel` Protocol defines the interface both agents satisfy — correct.

**Test results:** 31/31 passed, ruff clean, coverage 97.96% (target ≥90%).

---

## Phase 4: Separation Engine Core

**Goal:** Build the orchestration layer in `engine/demucs/` and `app/services/` that ties audio loading, inference, and postprocessing into a complete separation workflow.

### Deliverables

- [ ] `engine/demucs/__init__.py` — Public API exports
- [ ] `engine/demucs/separator.py` — `DemucsSeparator` class with `separate()` method
- [ ] `engine/demucs/config.py` — Separation configuration (model, stems, quality settings)
- [ ] `engine/demucs/errors.py` — Custom exceptions (`SeparationError`, `ModelLoadError`, `InferenceError`)
- [ ] `app/services/__init__.py` — Service layer public API
- [ ] `app/services/separation_service.py` — `SeparationService` orchestrating the full pipeline
- [ ] `app/services/__init__.py` — Service layer exports
- [ ] State machine for separation workflow (idle → loading → processing → complete → error)
- [ ] Progress reporting via signals/callbacks
- [ ] Integration tests for the full separation pipeline

### Skills Applied

- `python-backend-engineer` — Service layer pattern, dependency injection, error handling
- `audio-separation-specialist` — Artifact reduction, quality evaluation, SDR/SIR/SAR metrics
- `project-architect` — Module boundaries, FSM state management

### Key Patterns

```python
class SeparationService:
    def __init__(self, demucs_agent: DemucsAgent, audio_loader: AudioLoader):
        self._demucs = demucs_agent
        self._loader = audio_loader

    async def separate(self, file_path: Path) -> SeparationResult:
        audio = await self._loader.load(file_path)
        return await self._demucs.separate(audio)
```

### Quality Metrics

| Metric | Target |
| -------- | -------- |
| SDR (Signal-to-Distortion Ratio) | > 5 dB |
| SIR (Signal-to-Interference Ratio) | > 10 dB |
| SAR (Signal-to-Artifact Ratio) | > 10 dB |
| Separation time (3-min song, CPU) | < 30 seconds |
| Separation time (3-min song, GPU) | < 10 seconds |

---

## Phase 5: Export Pipeline

**Goal:** Implement the export capabilities in `engine/export/` — format conversion, metadata embedding, batch export, and quality optimization.

### Deliverables

- [ ] `engine/export/__init__.py` — Public API exports
- [ ] `engine/export/writer.py` — `ExportWriter` supporting WAV, FLAC, MP3, M4A
- [ ] `engine/export/config.py` — `ExportConfig` Pydantic model with format, bitrate, sample rate, metadata options
- [ ] `engine/export/metadata.py` — Metadata embedding (tags, artwork) via `mutagen`
- [ ] `engine/export/batch_exporter.py` — Batch export with progress tracking and error handling
- [ ] `engine/export/errors.py` — Export-specific exceptions
- [ ] Unit tests for export writer, batch exporter, and metadata embedding

### Skills Applied

- `export-pipeline-engineer` — Export pipeline design, format conversion, metadata embedding
- `audio-dsp-engineer` — Format conversion, quality optimization
- `python-backend-engineer` — Async file I/O with `aiofiles`, Pydantic models

### Supported Formats

| Format | Quality | Use Case |
| -------- | --------- | ---------- |
| WAV | Lossless, 16/24-bit PCM | Professional use |
| FLAC | Lossless, compression level 5 | Archiving |
| MP3 | Lossy, 192–320 kbps VBR | Sharing |
| M4A | Lossy, AAC encoding | Apple ecosystem |

---

## Phase 6: PySide6 UI Development

**Goal:** Build the desktop application UI with PySide6 — main window, file selection, processing controls, and settings.

### Deliverables

- [ ] `app/ui/__init__.py` — Layout definitions
- [ ] `app/ui/main_window.py` — `MainWindow` with menu bar, toolbar, status bar
- [ ] `app/ui/processing_dialog.py` — Progress dialog with cancel option and ETA
- [ ] `app/ui/settings_dialog.py` — Model selection, output format, performance settings
- [ ] `app/widgets/__init__.py` — Widget exports
- [ ] `app/widgets/file_drop_zone.py` — Drag-and-drop file selection widget
- [ ] `app/widgets/playback_controls.py` — Play/Pause/Stop/Seek controls
- [ ] `app/widgets/track_selector.py` — Vocals/Instrumental track selection
- [ ] `app/widgets/progress_bar.py` — Progress indicator with cancel
- [ ] `app/controllers/__init__.py` — Controller exports
- [ ] `app/controllers/main_controller.py` — UI logic and state binding
- [ ] `app/controllers/playback_controller.py` — Playback state management
- [ ] `app/models/__init__.py` — Data model exports
- [ ] `app/models/separation.py` — Pydantic models for separation state and results
- [ ] `app/resources/` — Icons, stylesheets (QSS), translations
- [ ] Dark/light theme support via QSS
- [ ] Responsive layout with `QSplitter`, `QStackedWidget`

### Skills Applied

- `pyside6-ui-engineer` — Widget design, signal/slot patterns, layout management, threading
- `ux-ui-designer` — Zero-typing UX, visual design language, interaction patterns
- `python-backend-engineer` — Async patterns, type hints, error handling
- `project-architect` — Module boundaries, state management

### Key Patterns

- **Signal/Slot:** Custom signals for inter-widget communication
- **Threading:** `QThread` or `QRunnable` for background processing — never block the UI thread
- **State:** Pydantic models + `enum.Enum` for FSM; state changes trigger UI updates via signals
- **Styling:** Qt Style Sheets (QSS) for theming, dark/light mode support

### UI Screens

| Screen | Purpose |
| -------- | --------- |
| Welcome | File selection, drag-and-drop, recent files |
| Processing | Progress bar, cancel button, estimated time |
| Results | Play separated tracks, export options |
| Settings | Model selection, output format, performance |

---

## Phase 7: Media Playback & Visualization

**Goal:** Implement audio playback for separated tracks with waveform visualization and full media controls.

### Deliverables

- [ ] `app/widgets/waveform_view.py` — Waveform visualization using `pyqtgraph`
- [ ] `app/widgets/equalizer.py` — Optional EQ display
- [ ] `app/controllers/playback_controller.py` — Playback state machine (stopped, playing, paused, loading, error)
- [ ] Independent volume control per track (vocals / instrumental)
- [ ] Seek slider with position indicator and time display
- [ ] Gapless playback support
- [ ] Playback state persistence across separation sessions
- [ ] Unit tests for playback controller and waveform widget

### Skills Applied

- `media-playback-engineer` — Audio playback, media controls, state management
- `pyside6-ui-engineer` — QtMultimedia integration, custom widget rendering
- `ux-ui-designer` — Interaction patterns, visual feedback

### Playback Stack

| Library | Purpose |
| --------- | --------- |
| `PySide6.QtMultimedia` | Qt audio playback |
| `sounddevice` | Low-latency audio output |
| `numpy` | Audio buffer manipulation |
| `pyqtgraph` | Real-time waveform rendering |

---

## Phase 8: Performance Optimization

**Goal:** Profile, benchmark, and optimize the application for speed, memory efficiency, and UI responsiveness.

### Deliverables

- [ ] CPU profiling with `cProfile` and `py-spy`
- [ ] Memory profiling with `memory_profiler`
- [ ] PyTorch profiling with `torch.profiler`
- [ ] System resource monitoring with `psutil`
- [ ] GPU optimization: `torch.cuda.amp.autocast()`, pinned memory, batch processing
- [ ] CPU optimization: `torch.set_num_threads()`, `torch.backends.mkldnn`, `torch.inference_mode()`
- [ ] Memory optimization: chunked processing, memory-mapped files, GPU memory release
- [ ] I/O optimization: async file operations, buffered reads, SSD temp storage
- [ ] UI responsiveness: ensure < 100ms interaction latency
- [ ] Benchmark suite with reproducible test cases
- [ ] Performance regression tests in CI

### Skills Applied

- `performance-engineer` — Profiling, benchmarking, optimization strategies
- `ai-ml-engineer` — PyTorch inference optimization, GPU acceleration
- `audio-dsp-engineer` — DSP pipeline optimization, chunked processing

### Performance Targets

| Metric | Target |
| -------- | -------- |
| Separation time (3-min song, CPU) | < 30 seconds |
| Separation time (3-min song, GPU) | < 10 seconds |
| Memory usage | < 4 GB peak |
| UI responsiveness | < 100ms for interactions |
| Startup time | < 3 seconds |
| File load time | < 5 seconds for 100 MB |

---

## Phase 9: Testing & Quality Assurance

**Goal:** Achieve the coverage targets across all layers with a comprehensive automated test suite.

### Deliverables

- [ ] `tests/conftest.py` — Shared fixtures, mock setup
- [ ] `tests/unit/engine/audio/` — Audio loader, resampler, preprocessor tests
- [ ] `tests/unit/engine/inference/` — Model manager, inference pipeline tests
- [ ] `tests/unit/engine/demucs/` — Separator, config, error handling tests
- [ ] `tests/unit/engine/export/` — Export writer, batch exporter, metadata tests
- [ ] `tests/unit/app/services/` — Separation service tests
- [ ] `tests/unit/app/controllers/` — Controller logic tests
- [ ] `tests/unit/app/widgets/` — Widget unit tests
- [ ] `tests/integration/` — Full pipeline integration tests
- [ ] `tests/ui/` — UI behavior tests with `pytest-qt`
- [ ] `tests/fixtures/` — Small audio files (< 1 MB), synthetic audio for edge cases
- [ ] Mock external dependencies (file system, network, HuggingFace)
- [ ] Coverage report generation with `pytest-cov`
- [ ] Coverage gates: engine ≥ 90%, app ≥ 85%, UI ≥ 70%, overall ≥ 85%

### Skills Applied

- `qa-automation-engineer` — Test strategy, framework setup, coverage targets
- `testing-engineer` — Test patterns, mock strategies, CI integration
- `python-backend-engineer` — Async test patterns with `pytest-asyncio`

### Test Structure

```text
tests/
├── unit/
│   ├── engine/
│   │   ├── audio/
│   │   ├── inference/
│   │   ├── demucs/
│   │   └── export/
│   ├── app/
│   │   ├── services/
│   │   ├── controllers/
│   │   └── widgets/
│   └── conftest.py
├── integration/
│   ├── test_pipeline.py
│   └── test_file_io.py
├── ui/
│   ├── test_main_window.py
│   └── test_playback_controls.py
└── fixtures/
    └── (small audio files)
```

---

## Phase 10: Packaging & Distribution

**Goal:** Build cross-platform distributable packages with code signing and automated release pipelines.

### Deliverables

- [ ] `descombinator.spec` — PyInstaller spec file with hidden imports and data files
- [ ] Windows build: PyInstaller → `.exe` installer (NSIS)
- [ ] macOS build: PyInstaller → `.dmg` and `.pkg` (code signed, notarized)
- [ ] Linux build: PyInstaller → `.AppImage`, `.deb`, `.rpm`
- [ ] GitHub Actions CI workflow for automated testing on all platforms
- [ ] GitHub Actions build workflow triggered on release tags
- [ ] Code signing configuration (Windows `signtool`, macOS `codesign` + notarization)
- [ ] Release checklist automation (tests → build → sign → upload → docs → announce)
- [ ] Semantic versioning (MAJOR.MINOR.PATCH) with Git tags
- [ ] Changelog generation from commit messages

### Skills Applied

- `packaging-distribution-engineer` — Packaging, code signing, release management
- `cross-platform-engineer` — Platform-specific builds, CI/CD matrix
- `devops-engineer` — CI/CD pipelines, GitHub Actions workflows
- `project-architect` — Build configuration, dependency bundling

### Supported Platforms

| Platform | Version | Architecture |
| ---------- | --------- | ------------- |
| Windows | 10, 11 | x64 |
| macOS | 12+ | ARM64, x64 |
| Linux | Ubuntu 22.04+, Fedora 38+ | x64, ARM64 |

---

## Phase 11: Documentation & Release

**Goal:** Produce comprehensive user-facing and developer-facing documentation, then publish the first stable release.

### Deliverables

- [ ] `docs/architecture/` — Architecture Decision Records (ADRs), dependency diagrams
- [ ] `docs/api/` — API reference generated from docstrings
- [ ] `docs/guides/` — User guides: installation, quick start, feature walkthroughs
- [ ] `docs/development/` — Developer setup, contribution guidelines, testing guide
- [ ] `docs/troubleshooting/` — Common issues, error codes, solutions
- [ ] `docs/license-compliance/` — License documentation for code and model weights
- [ ] `docs/roadmap.md` — This file (kept up to date)
- [ ] Sphinx or MkDocs static documentation site
- [ ] Inline docstrings on all public modules, classes, and methods
- [ ] README.md updated with final feature set and screenshots
- [ ] First stable release published to GitHub Releases
- [ ] Distribution on appropriate channels (Flathub, Microsoft Store, Mac App Store)

### Skills Applied

- `documentation-writer` — Documentation standards, user guides, API docs
- `technical-writer` — Technical writing, code examples, style guide
- `devops-engineer` — Release automation, changelog generation
- `project-architect` — Architecture documentation, ADRs

### Documentation Standards

- **Format:** Markdown (primary), Sphinx/MkDocs for generated site
- **Style:** Clear, concise, active voice, present tense
- **Code examples:** Every public API documented with usage examples
- **Maintenance:** Update documentation with every code change; review in PRs

---

## Milestone Summary

| Milestone | Phases | Status |
| ----------- | -------- | -------- |
| Environment & Foundation | 1 | ✅ Complete |
| Audio I/O & DSP Pipeline | 2 | ✅ Complete |
| ML Model Integration | 3 | ✅ Complete |
| Separation Engine | 4 | 🔲 Planned |
| Export Pipeline | 5 | 🔲 Planned |
| Desktop UI | 6 | 🔲 Planned |
| Playback & Visualization | 7 | 🔲 Planned |
| Performance Optimization | 8 | 🔲 Planned |
| Testing & QA | 9 | 🔲 Planned |
| Packaging & Distribution | 10 | 🔲 Planned |
| Documentation & Release | 11 | 🔲 Planned |

---

## Dependency Graph

```text
Phase 1 (Foundation)
 ├── Phase 2 (Audio I/O & DSP)
 │    └── Phase 3 (ML Model Integration)
 │         └── Phase 4 (Separation Engine)
 │              ├── Phase 5 (Export Pipeline)
 │              └── Phase 6 (PySide6 UI)
 │                   ├── Phase 7 (Playback & Visualization)
 │                   └── Phase 8 (Performance Optimization)
 └── Phase 9 (Testing & QA) ← depends on Phases 1–8
      └── Phase 10 (Packaging & Distribution) ← depends on Phase 9
           └── Phase 11 (Documentation & Release) ← depends on Phase 10
```

---

## Git Workflow

All work follows the branching strategy defined in AGENTS.md:

- **Base branch:** `develop`
- **Feature branches:** `feature/phase-XX-short-name`
- **Bugfix branches:** `bugfix/issue-description`
- **Hotfix branches:** `hotfix/issue-description`
- **Commit format:** `type(scope): subject` (e.g., `feat(audio): add AudioLoader with MP3 support`)
- **PR process:** Create from feature branch → assign reviewers → merge to `develop`
- **Release:** Tag on `master` with semantic version

---

## License Note

The license for the code and the AI model weights may differ. Before distributing a public release, review all dependencies, model weights, and their respective usage terms.
