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
- [x] `pyproject.toml` with project metadata and tool configuration
- [x] `.envrc` and `activate.sh` for environment auto-activation
- [x] `main.py` async entry point
- [ ] Ruff linting and formatting configuration
- [ ] Pre-commit hooks (ruff, mypy)
- [ ] GitHub Actions CI workflow (lint + typecheck on push)
- [ ] Git branching strategy documented (`develop` → `feature/*`, `bugfix/*`, `hotfix/*`)
- [ ] Commit convention enforced (`type(scope): subject`)
- [ ] `.gitignore` with venv, cache, and build artifacts

### Skills Applied

- `python-backend-engineer` — Coding standards, async patterns, type hints
- `devops-engineer` — CI/CD scaffolding, environment configuration
- `project-architect` — Module boundaries, dependency graph

### Key Decisions

- **Architecture:** Modular monolith with clear `app/` ↔ `engine/` layer separation
- **State management:** Pydantic models + `enum.Enum` for FSM state machines
- **Logging:** `loguru` exclusively, no `logging.basicConfig()`
- **Async-first:** All I/O operations use `async def`

---

## Phase 2: Audio I/O & DSP Pipeline

**Goal:** Implement the audio loading, resampling, format conversion, and preprocessing capabilities in `engine/audio/`.

### Deliverables

- [ ] `engine/audio/__init__.py` — Public API exports
- [ ] `engine/audio/loader.py` — `AudioLoader` class with async `load()` supporting MP3, WAV, FLAC, M4A, OGG
- [ ] `engine/audio/resampler.py` — Resampling using `resampy` with `sinc_best` quality, target 44.1 kHz
- [ ] `engine/audio/preprocessor.py` — DC offset removal, peak normalization to -1 dBFS, optional spectral gating
- [ ] `engine/audio/postprocessor.py` — Artifact reduction (windowing, crossfading), peak limiting
- [ ] `engine/audio/metadata.py` — Metadata reading/writing via `mutagen`
- [ ] Unit tests for all audio I/O modules (`tests/unit/engine/audio/`)
- [ ] Test fixtures in `tests/fixtures/` (small audio files < 1 MB)

### Skills Applied

- `audio-dsp-engineer` — DSP pipeline design, format handling, preprocessing/postprocessing
- `python-backend-engineer` — Async I/O with `aiofiles`, type hints, error handling
- `model-manager` — Model weight storage conventions

### Key Patterns

```python
# AudioLoader interface
class AudioLoader:
    async def load(self, path: Path, sr: int = 44100) -> np.ndarray: ...
    async def load_metadata(self, path: Path) -> dict[str, Any]: ...
```

### Quality Targets

- Support all major audio formats (MP3, WAV, FLAC, M4A, OGG)
- Resample to 44.1 kHz (Demucs native) with high-quality `sinc_best`
- Preserve original metadata on export

---

## Phase 3: ML Model Integration & Inference

**Goal:** Integrate Demucs and Open-Unmix models, build the inference pipeline in `engine/inference/`, and implement model lifecycle management.

### Deliverables

- [ ] `engine/inference/__init__.py` — Public API exports
- [ ] `engine/inference/demucs_agent.py` — Demucs v4 integration with `htdemucs_ft` and `mdx_extra` presets
- [ ] `engine/inference/openunmix_agent.py` — Open-Unmix `umxhq` integration
- [ ] `engine/inference/pipeline.py` — `InferencePipeline` orchestrating preprocessing → model → postprocessing
- [ ] `engine/inference/model_manager.py` — `ModelManager` for download, cache, versioning, and runtime switching
- [ ] `engine/inference/weights/` — Directory for cached model weights
- [ ] Model integrity verification with SHA-256 checksums
- [ ] HuggingFace `huggingface_hub` integration for model downloads
- [ ] GPU support with `torch.cuda.amp.autocast()` and mixed precision
- [ ] CPU optimization with `torch.set_num_threads()`, `torch.backends.mkldnn`
- [ ] Unit tests for inference pipeline and model manager

### Skills Applied

- `ai-ml-engineer` — Model integration, PyTorch optimization, inference pipeline design
- `model-manager` — Model lifecycle, caching, versioning, switching
- `audio-separation-specialist` — Model selection, quality evaluation, artifact reduction
- `python-backend-engineer` — Async patterns, error handling, dependency injection

### Key Patterns

```python
class InferencePipeline:
    def __init__(self, model_manager: ModelManager):
        self._model_manager = model_manager

    async def run(
        self, audio: np.ndarray, model_name: str = "htdemucs_ft"
    ) -> SeparationResult:
        model = await self._model_manager.get_model(model_name)
        with torch.inference_mode():
            return model(audio)
```

### Model Stack

| Model | Purpose | Backend | Size |
| ------- | --------- | --------- | ------ |
| Demucs v4 (`htdemucs_ft`) | Primary separation | PyTorch | ~120 MB |
| Demucs v4 (`mdx_extra`) | High-quality alternative | PyTorch | ~200 MB |
| Open-Unmix (`umxhq`) | Secondary/alternative | PyTorch | ~50 MB |

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
| Audio I/O & DSP Pipeline | 2 | 🔲 Planned |
| ML Model Integration | 3–4 | 🔲 Planned |
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
