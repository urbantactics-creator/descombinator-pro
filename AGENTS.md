# AGENTS.md — Descombinator Pro

> **Agent Instructions for Descombinator Pro**
>
> This file provides guidance for AI agents working on the Descombinator Pro codebase.
> It is **not** a user-facing document. Refer to `readme.md` for user documentation.

## Project Overview

Descombinator Pro is a desktop application that separates audio into **vocals** and **instrumental** tracks using AI, entirely on-device. Built with Python 3.12+, PySide6, PyTorch, and Demucs.

## Architecture

```
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
│   └── export/             # Result export and file writing
├── tests/                  # Unit, integration, and UI tests
├── docs/                   # Documentation
├── assets/                 # Project assets
├── .kilo/skills/           # Specialized agent skills
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project configuration
└── .envrc                # direnv auto-activation
```

## Module Boundaries

- **`app/`** — Presentation layer. No direct engine calls; communicates via services.
- **`engine/`** — Processing layer. No UI dependencies. Pure async Python.
- **`app/services/`** — Orchestration layer. Coordinates between `app/` and `engine/`.

## Coding Standards

### Python

- **Python 3.12+** — Use modern type hints (`X | None`, not `Optional[X]`)
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
- **Coverage**: 85% minimum for engine, 70% for UI
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

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FILE` | None | Log file path |
| `MODEL_CACHE_DIR` | `~/.cache/descombinator` | Model weights cache |
| `MAX_WORKERS` | CPU count | Parallel processing workers |

## Skills

This project includes specialized agent skills in `.kilo/skills/`. Each skill provides domain-specific guidance. Key skills for this project:

- **project-architect** — System architecture and module decomposition
- **python-backend-engineer** — Python coding standards and patterns
- **ai-ml-engineer** — ML model integration and optimization
- **audio-dsp-engineer** — Audio processing and DSP
- **pyside6-ui-engineer** — PySide6 UI development
- **qa-automation-engineer** — Testing strategy and automation
- **code-reviewer** — Code review checklist and standards
- **security-auditor** — Security best practices and auditing
- **devops-engineer** — CI/CD and deployment
- **documentation-writer** — Documentation standards

## Useful Commands

```bash
# Activate venv
source activate.sh

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Run tests
pytest tests/

# Build distributable
pyinstaller --onefile --windowed descombinator.spec

# Lint and format
ruff check .
ruff format .
```

## Resources

- [Demucs Documentation](https://github.com/facebookresearch/demucs)
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [Librosa Documentation](https://librosa.org/doc/)
