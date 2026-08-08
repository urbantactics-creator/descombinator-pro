# AGENTS.md — Descombinator Pro

> **Agent Instructions for Descombinator Pro**
>
> This file provides guidance for AI agents working on the Descombinator Pro codebase.
> It is **not** a user-facing document. Refer to `README.md` for user documentation.

## Project Overview

Descombinator Pro is a desktop application that separates audio into **vocals** and **instrumental** tracks using AI, entirely on-device. Built with Python 3.14+, PySide6, PyTorch, and Demucs.

## Architecture

```text
descombinator/
├── app/                    # Presentation layer
│   ├── ui/                 # Layout definitions
│   ├── widgets/            # Custom reusable widgets
│   ├── controllers/        # UI logic and state binding
│   ├── models/             # Data models (Pydantic)
│   ├── services/           # Business logic services
│   └── resources/          # Icons, translations, static assets
├── engine/                 # Processing layer
│   ├── demucs/             # Demucs separation backend
│   ├── inference/          # Model inference pipeline
│   ├── audio/              # Audio loading and processing
│   ├── export/             # Result export and file writing
│   └── performance/        # Profiling, monitoring, runtime optimization
├── benchmarks/             # Performance benchmark suite + baselines.json
├── scripts/                # Dev tooling (bench regression gate, profiling)
├── tests/                  # Unit, integration, and UI tests
├── docs/                   # Documentation
├── assets/                 # Project assets
├── .kilo/skills/           # Specialized agent skills
├── main.py                 # Application entry point
├── pyproject.toml          # Project configuration (single source of truth for dependencies)
└── .envrc                  # direnv auto-activation
```

## Module Boundaries

- **`app/`** — Presentation layer. No direct engine calls; communicates via services.
- **`engine/`** — Processing layer. No UI dependencies. Pure async Python.
- **`app/services/`** — Orchestration layer. Coordinates between `app/` and `engine/`.

## Coding Standards

### Python

- **Python 3.14+** — Use modern type hints (`X | None`, not `Optional[X]`)
- **Async-first** — All I/O operations use `async def`
- **Type hints** — Required on all function signatures
- **Docstrings** — Module-level and class-level docstrings required
- **Logging** — Use `loguru` (`from loguru import logger`)
- **No `logging.basicConfig()`** — Use `loguru` configuration instead

### File Structure

- One class per file (unless closely related)
- `__init__.py` exports public API
- Tests mirror source structure: `tests/unit/engine/audio/test_loader.py`

## Key Patterns

### Service Layer

```python
class SeparationService:
    def __init__(self, demucs_agent: DemucsAgent, audio_loader: AudioLoader):
        self._demucs = demucs_agent
        self._loader = audio_loader

    async def separate(self, file_path: Path) -> SeparationResult:
        audio = await self._loader.load(file_path)
        return await self._demucs.separate(audio)
```

### State Management

- Use `pydantic.BaseModel` for state models
- Use `enum.Enum` for state machines
- State changes trigger UI updates via signals

### Error Handling

```python
try:
    result = await self._demucs.separate(audio)
except DemucsError as e:
    logger.error(f"Separation failed: {e}")
    raise SeparationError(str(e)) from e
```

## Testing

- **Framework**: `pytest` with `pytest-asyncio` and `pytest-qt`
- **Coverage**: 85% minimum for engine, 70% for UI (Phase 9 will raise these)
- **Current status**: 308 unit/integration tests passing, 17 UI tests passing
- **Test data**: Store in `tests/fixtures/`, use small files (< 1 MB)
- **Mocking**: Mock external dependencies (file system, network, models)

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov=engine --cov-report=term-missing

# Run only unit tests
pytest tests/unit/

# Run only UI tests
pytest tests/ui/
```

## Phase Status

| Phase | Name                             | Status         |
|-------|----------------------------------|----------------|
| 1     | Project Foundation               | ✅ Complete    |
| 2     | Audio I/O & DSP Pipeline         | ✅ Complete    |
| 3     | ML Model Integration & Inference | ✅ Complete    |
| 4     | Separation Engine Core           | ✅ Complete    |
| 5     | Export Pipeline                  | ✅ Complete    |
| 6     | PySide6 UI Development           | ✅ Complete    |
| 7     | Media Playback & Visualization   | ✅ Complete    |
| 8     | Performance Optimization         | ✅ Complete    |
| 9     | Testing & Quality Assurance      | ⚠️ Partial     |
| 10    | Packaging & Distribution         | ❌ Not Started |
| 11    | Documentation & Release          | ❌ Not Started |

## CI (GitHub Actions)

- **Workflow**: `.github/workflows/ci.yml` — two jobs: `lint-and-test` and `benchmark` (benchmark `needs: lint-and-test`).
- **System dependencies** (PySide6/QtMultimedia on Ubuntu runners): `libegl1 libgl1 libopengl0 libpulse0 ffmpeg xvfb`.
- **Headless Qt**: unit/integration tests run with `QT_QPA_PLATFORM=offscreen`; UI tests run under `xvfb-run`.
- **Coverage thresholds in CI**: unit/integration `--cov-fail-under=85`, UI `--cov-fail-under=70` (Phase 9 will raise them).
- **Benchmark gate**: `benchmarks/` suite (16 non-slow gates) + `scripts/bench/check_regressions.py` fails on > 100 % median regression (REGRESSION_RATIO=2.0) vs `benchmarks/baselines.json` or a missed absolute target. Baselines are committed with worst-case observed values across multiple CI runs to absorb shared-runner variance.
- **Mypy**: strict mode; pre-existing Phase 6/7 drift (Qt/Pydantic `Any` bases) is scoped via `[[tool.mypy.overrides]]` in `pyproject.toml`.

## Git Workflow

- **Branch**: `feature/*`, `bugfix/*`, `hotfix/*` from `develop`
- **Commit format**: `type(scope): subject` (e.g., `feat(separation): add Demucs v4`)
- **PR**: Create from feature branch, assign reviewers, merge to `develop`
- **Main branch**: `master` (protected, production releases only)

## Environment

### Virtual Environment

```bash
# Auto-activates via .envrc (direnv) or activate.sh
source activate.sh
```

### Environment Variables

| Variable           | Default                  | Description                 |
|--------------------|--------------------------|-----------------------------|
| `LOG_LEVEL`        | `INFO`                   | Logging level               |
| `LOG_FILE`         | None                     | Log file path               |
| `MODEL_CACHE_DIR`  | `~/.cache/descombinator` | Model weights cache         |
| `MAX_WORKERS`      | CPU count                | Parallel processing workers |

## Skills

This project includes specialized agent skills in `.kilo/skills/`. Each skill provides domain-specific guidance. Key skills for this project:

- **project-architect** — System architecture and module decomposition
- **python-backend-engineer** — Python coding standards and patterns
- **ai-ml-engineer** — ML model integration and optimization
- **audio-dsp-engineer** — Audio processing and DSP
- **audio-separation-specialist** — Audio source separation techniques and quality evaluation
- **pyside6-ui-engineer** — PySide6 UI development
- **media-playback-engineer** — Audio playback, media controls, and state management
- **export-pipeline-engineer** — Export pipeline design, format conversion, metadata embedding
- **qa-automation-engineer** — Testing strategy, framework setup, coverage gates
- **testing-engineer** — Test automation, test data management, CI testing
- **code-reviewer** — Code review checklist and standards
- **security-auditor** — Security best practices and auditing
- **devops-engineer** — CI/CD and deployment
- **performance-engineer** — Profiling, benchmarking, and optimization
- **documentation-writer** — Technical documentation and user guides
- **technical-writer** — Specifications, release notes, and technical communication
- **configuration-manager** — Application configuration and environment management
- **dependency-manager** — Python dependency management and security auditing
- **packaging-distribution-engineer** — Application packaging and distribution
- **cross-platform-engineer** — Cross-platform compatibility and platform-specific builds

## Useful Commands

```bash
# Activate venv
source activate.sh

# Install dependencies
pip install .[dev]

# Run the application
python main.py

# Run tests
pytest tests/

# Build distributable
pyinstaller --onefile --windowed descombinator.spec

# Lint and format
ruff check .
ruff format .

# Security audit
pip-audit

# Run benchmarks (non-slow gates)
pytest benchmarks/ -m "not slow" --benchmark-only

# Check benchmark regressions vs baselines
python -m scripts.bench.check_regressions --baseline benchmarks/baselines.json --result bench_results.json --min-rounds 10 --max-time 1.0 --warmup on --calibration-precision 3

# Profile memory / torch (slow, real model)
python -m scripts.profiling.profile_memory
python -m scripts.profiling.profile_torch
```

## Resources

- [Demucs Documentation](https://github.com/facebookresearch/demucs)
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [Librosa Documentation](https://librosa.org/doc/)
