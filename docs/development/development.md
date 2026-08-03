# Development Guide

This guide covers the development workflow for Descombinator Pro.

## Quick Start

```bash
# Clone and enter the project
git clone <repo-url>
cd descombinator

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install .[dev]

# Install pre-commit hooks
pre-commit install

# Run the application
python main.py
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/phase-XX-short-name
```

### 2. Make Changes

Follow the coding standards in [AGENTS.md](../AGENTS.md):

- Python 3.12+ with modern type hints (`X | None`, not `Optional[X]`)
- Async-first: all I/O operations use `async def`
- Type hints required on all function signatures
- Module-level and class-level docstrings required
- Use `loguru` for logging (`from loguru import logger`)
- One class per file (unless closely related)

### 3. Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov=engine --cov-report=term-missing

# Run only unit tests
pytest tests/unit/

# Run only UI tests (headless)
QT_QPA_PLATFORM=offscreen pytest tests/ui/
```

### 4. Run Code Quality Checks

```bash
# Lint
ruff check .

# Format
ruff format .

# Type checking
mypy .

# Security audit
pip-audit

# Run all pre-commit hooks
pre-commit run --all-files
```

### 5. Run Benchmarks

```bash
# Run benchmark suite (non-slow gates)
pytest benchmarks/ -m "not slow" --benchmark-only

# Check regressions against committed baselines
python -m scripts.bench.check_regressions --baseline benchmarks/baselines.json --result bench_results.json
```

### 6. Commit and Push

```bash
git add .
git commit -m "type(scope): subject"
git push origin feature/phase-XX-short-name
```

### 7. Create a Pull Request

Create a PR to `develop` and assign reviewers.

## Profiling

### CPU Profiling

```bash
# cProfile
.venv/bin/python scripts/profiling/profile_cpu.py
.venv/bin/python -m snakeviz <pstats-output>

# py-spy (sampling profiler)
.venv/bin/python scripts/profiling/profile_pyspy.py
py-spy record --pid <PID> -o cpu.svg --duration 60
```

### Memory Profiling

```bash
.venv/bin/python scripts/profiling/profile_memory.py
mprof run .venv/bin/python scripts/profiling/_mem_runner.py
mprof plot -o reports/memory.png
```

### PyTorch Profiling

```bash
.venv/bin/python scripts/profiling/profile_torch.py
# Open trace.json in chrome://tracing or tensorboard
```

### Startup Time

```bash
.venv/bin/python scripts/profiling/measure_startup.py
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FILE` | None | Log file path |
| `MODEL_CACHE_DIR` | `~/.cache/descombinator` | Model weights cache |
| `MAX_WORKERS` | CPU count | Parallel processing workers |

## System Dependencies

### Linux (Ubuntu/Debian)

```bash
sudo apt-get install -y libegl1 libgl1 libopengl0 libpulse0 ffmpeg xvfb
```

### macOS

```bash
brew install ffmpeg
```

### Windows

Install [FFmpeg](https://ffmpeg.org/download.html) and add to PATH.
