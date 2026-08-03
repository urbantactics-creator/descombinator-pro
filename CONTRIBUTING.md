# Contributing to Descombinator Pro

Thank you for your interest in contributing to Descombinator Pro! This document outlines the process for setting up a development environment, coding standards, and the contribution workflow.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Git Workflow](#git-workflow)
- [Pull Request Process](#pull-request-process)
- [Performance Benchmarks](#performance-benchmarks)
- [Documentation](#documentation)

## Development Setup

### Prerequisites

- Python 3.12+
- pip
- System dependencies (Linux): `libegl1 libgl1 libopengl0 libpulse0 ffmpeg`
- [direnv](https://direnv.net/) (optional, for auto-activation)

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd descombinator

# Create and activate the virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

> **Tip:** If you have direnv installed, the `.envrc` file will auto-activate the venv when you enter the project directory.

## Project Structure

```text
descombinator/
├── app/                    # Presentation layer (UI, controllers, widgets)
│   ├── ui/                 # Layout definitions
│   ├── widgets/            # Custom reusable widgets
│   ├── controllers/        # UI logic and state binding
│   ├── models/             # Data models (Pydantic)
│   ├── services/           # Business logic services
│   └── resources/          # Icons, translations, static assets
├── engine/                 # Processing layer (no UI dependencies)
│   ├── demucs/             # Demucs separation backend
│   ├── inference/          # Model inference pipeline
│   ├── audio/              # Audio loading and processing
│   ├── export/             # Result export and file writing
│   └── performance/        # Profiling, monitoring, runtime optimization
├── benchmarks/             # Performance benchmark suite
├── scripts/                # Dev tooling (profiling, benchmark checks)
├── tests/                  # Unit, integration, and UI tests
├── docs/                   # Documentation
├── .kilo/skills/           # Specialized agent skills
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Dev dependencies
├── pyproject.toml          # Project configuration
├── .envrc                  # direnv auto-activation
└── activate.sh             # Manual venv activation script
```

### Module Boundaries

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
- **One class per file** (unless closely related)
- **`__init__.py`** exports public API

### Commit Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): subject
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `build`, `ci`

Examples:

```
feat(audio): add AudioLoader with MP3 support
fix(playback): resolve gapless mixing bug
docs(perf): add performance tuning guide
```

## Testing

### Running Tests

```bash
# All tests
pytest tests/

# With coverage
pytest tests/ --cov=app --cov=engine --cov-report=term-missing

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# UI tests (headless)
QT_QPA_PLATFORM=offscreen pytest tests/ui/

# UI tests (with xvfb)
xvfb-run -a pytest tests/ui/
```

### Test Structure

```text
tests/
├── unit/
│   ├── engine/
│   │   ├── audio/
│   │   ├── inference/
│   │   ├── demucs/
│   │   └── export/
│   └── app/
│       ├── services/
│       ├── controllers/
│       └── widgets/
├── integration/
├── ui/
└── fixtures/
```

### Test Data

- Store test data in `tests/fixtures/`
- Use small files (< 1 MB)
- Mock external dependencies (file system, network, models)

### Coverage Targets

| Layer | Target |
| ------- | -------- |
| Engine | ≥ 90% |
| App | ≥ 85% |
| UI | ≥ 70% |
| Overall | ≥ 85% |

## Code Quality

### Linting

```bash
ruff check .
```

### Formatting

```bash
ruff format .
```

### Type Checking

```bash
mypy .
```

### Pre-commit Hooks

Pre-commit hooks run automatically on commit. To run manually:

```bash
pre-commit run --all-files
```

Hooks include:

- `ruff` (lint)
- `ruff-format` (formatting)
- `trailing-whitespace`
- `end-of-file-fixer`
- `check-yaml`
- `check-toml`
- `check-merge-conflict`
- `large-files`

## Git Workflow

### Branching Strategy

- **Base branch:** `develop`
- **Feature branches:** `feature/phase-XX-short-name`
- **Bugfix branches:** `bugfix/issue-description`
- **Hotfix branches:** `hotfix/issue-description`

### Process

1. Create a feature branch from `develop`
2. Make your changes with clear, atomic commits
3. Run tests and code quality checks
4. Create a pull request to `develop`
5. Assign reviewers
6. Address feedback
7. Merge to `develop`

### Release Process

- Tag releases on `master` with semantic versioning (`v1.0.0`)
- `master` is protected (production releases only)
- `develop` is the integration branch

## Performance Benchmarks

The project includes a benchmark suite with a CI regression gate.

```bash
# Run benchmark suite (non-slow gates)
pytest benchmarks/ -m "not slow" --benchmark-only

# Check regressions against committed baselines
python -m scripts.bench.check_regressions --baseline benchmarks/baselines.json --result bench_results.json
```

The regression gate fails on:

- > 20% median regression vs `benchmarks/baselines.json`
- A missed absolute target

Update baselines only after an intentional optimization:

```bash
# Regenerate baselines (after intentional optimization)
pytest benchmarks/ -m "not slow" --benchmark-only --benchmark-json=benchmarks/baselines.json
```

## Documentation

### Documentation Structure

```text
docs/
├── architecture/       → System architecture and ADRs
├── api/                → API reference
├── guides/             → User and developer guides
├── development/        → Development setup and contribution guidelines
├── troubleshooting/    → Common issues and solutions
└── license-compliance/ → License documentation
```

### Documentation Standards

- Use clear, concise language
- Write in active voice, present tense
- Include code examples
- Link to related documentation
- Update documentation with every code change

### Changelog

All notable changes are documented in [CHANGELOG.md](CHANGELOG.md).

## License

The license for the code and the AI model weights may differ. Before distributing a public release, review all dependencies, model weights, and their respective usage terms.
