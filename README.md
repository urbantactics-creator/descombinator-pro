# Descombinator Pro

Separate any song into vocals and instrumental tracks — fast, free, and private.
No internet required, no file uploads. Studio-quality results in seconds.

## Who is this for?

- 🎵 **Musicians** wanting stems for remixing
- 🎬 **Content creators** needing clean instrumentals
- 🎛️ **Producers** needing high-quality stems

## Project Status

| Milestone | Status |
|-----------|--------|
| Vocal ↔ Instrumental separation | ✅ Complete |
| Multi-instrument separation (Demucs) | ✅ Complete |
| Playback & waveform visualization | ✅ Complete |
| Export pipeline (WAV, FLAC, MP3, M4A) | ✅ Complete |
| Performance optimization (benchmarks, baselines, CI regression gate) | ✅ Complete |
| Testing & QA (665 tests — 564 unit/integration @ 87.69% + 101 UI @ 78.27%, CI fully green) | ✅ Complete |
| Packaging & distribution | ⚠️ In Progress |
| Documentation & release | ⚠️ In Progress |

## Features

- **High-quality separation** powered by Demucs (htdemucs_ft, mdx_extra) and Open-Unmix (umxhq)
- **Modern, minimal UI** built with PySide6 — dark/light theme support
- **Fast local processing** with PyTorch acceleration
- **On-device privacy** — no files uploaded to the internet
- **Synchronized multi-track playback** with per-track volume/mute, seek, and gapless mixing
- **Waveform visualization** with playback position tracking
- **Multi-format export** — WAV, FLAC, MP3, M4A with metadata embedding
- **Performance-tested** — 16 benchmark gates enforced in CI (regression gate fails on > 20 % median drift)
- **Thermal monitoring** — cross-platform CPU/GPU temperature sampling with graceful degradation and thermal throttling
- **Cross-platform** support (Linux, macOS, Windows)
- **Modular, production-ready** codebase with async-first architecture

## Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.12+ |
| GUI Framework | PySide6 ≥6.11 |
| ML Backend | PyTorch ≥2.13, TorchAudio ≥2.11 |
| Separation | Demucs ≥4.1, Open-Unmix ≥1.3 |
| Audio I/O | Librosa ≥0.11, SoundFile ≥0.14, Resampy ≥0.4.3 |
| Metadata | Mutagen ≥1.48 |
| Visualization | PyQtGraph ≥0.14 |
| Async I/O | aiofiles ≥25.1 |
| Logging | Loguru ≥0.7.3 |
| Configuration | Pydantic ≥2.13, python-dotenv ≥1.2, PyYAML ≥6.0 |
| Testing | pytest ≥9.1, pytest-qt ≥4.5, pytest-asyncio ≥1.4, pytest-cov ≥7.1, pytest-benchmark ≥5.2 |
| Code Quality | ruff ≥0.16, mypy ≥2.3, pre-commit ≥4.6 |
| Profiling | memory-profiler ≥0.61, py-spy ≥0.4, snakeviz ≥2.2 |
| Packaging | PyInstaller ≥6.21 |

## Project Structure

```text
descombinator/
├── app/
│   ├── ui/           # UI components and layouts
│   ├── widgets/      # Custom reusable widgets
│   ├── controllers/  # Application logic and state management
│   ├── models/       # Data models and schemas
│   ├── services/     # Business logic services
│   └── resources/    # Icons, translations, static assets
├── engine/
│   ├── demucs/       # Demucs separation backend
│   ├── inference/    # Model inference pipeline
│   ├── audio/        # Audio loading and processing
│   ├── export/       # Result export and file writing
│   └── performance/  # Profiling, monitoring, runtime optimization
├── benchmarks/       # Performance benchmark suite + baselines.json
├── scripts/          # Dev tooling (bench regression gate, profiling)
├── tests/            # Unit, integration, and UI tests
├── docs/             # Documentation
├── assets/           # Project assets
├── .kilo/skills/    # Specialized agent skills
├── main.py           # Application entry point
├── pyproject.toml    # Project configuration (single source of truth for dependencies)
├── .envrc            # direnv auto-activation
└── activate.sh       # Manual venv activation script
```

## Installation

### Prerequisites

- Python 3.12+
- pip
- System dependencies (Linux): `libegl1 libgl1 libopengl0 libpulse0 ffmpeg`

### Quick Install

```bash
# Create and activate the virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install .[dev]
```

> **Tip:** If you have [direnv](https://direnv.net/) installed, the `.envrc` file will auto-activate the venv when you enter the project directory.

### Download

Prebuilt installers are available on the [Releases](https://github.com/descombinator/descombinator/releases) page. No Python or command line required.

## Usage

```bash
# With venv activated
python main.py
```

## Development

### Running Tests

```bash
# All tests
pytest tests/

# With coverage
pytest tests/ --cov=app --cov=engine --cov-report=term-missing

# Unit tests only
pytest tests/unit/

# UI tests (headless)
QT_QPA_PLATFORM=offscreen pytest tests/ui/
```

### Code Quality

```bash
# Lint
ruff check .

# Format
ruff format .

# Type checking
mypy .
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

### Building a Distributable

```bash
pyinstaller --onefile --windowed descombinator.spec
```

### Benchmarks

```bash
# Run benchmark suite (non-slow gates)
pytest benchmarks/ -m "not slow" --benchmark-only

# Check regressions against committed baselines
python -m scripts.bench.check_regressions --baseline benchmarks/baselines.json --result bench_results.json
```

## Performance

Phase 8 (Performance Optimization) is delivered. CI runs a benchmark regression gate:

```bash
# Run the benchmark suite (non-slow gates)
pytest benchmarks/ -m "not slow" --benchmark-only

# Check regressions against committed baselines
python -m scripts.bench.check_regressions --baseline benchmarks/baselines.json --result bench_results.json
```

Key results (real CI medians): startup import ~1.09 s (target < 3 s), playback interactions < 0.1 ms, waveform decimation ~2.1 ms, memory peak 133 MB (target < 4 GB). See `roadmap.md` (Phase 8) and `docs/development/performance/` for details.

## Roadmap

See [roadmap.md](roadmap.md) for the full phase-by-phase plan.

| Phase | Name | Status |
|-------|------|--------|
| 1 | Project Foundation | ✅ Complete |
| 2 | Audio I/O & DSP Pipeline | ✅ Complete |
| 3 | ML Model Integration & Inference | ✅ Complete |
| 4 | Separation Engine Core | ✅ Complete |
| 5 | Export Pipeline | ✅ Complete |
| 6 | PySide6 UI Development | ✅ Complete |
| 7 | Media Playback & Visualization | ✅ Complete |
| 8 | Performance Optimization | ✅ Complete |
| 9 | Testing & Quality Assurance | ✅ Complete |
| 10 | Packaging & Distribution | 🔲 Planned |
| 11 | Documentation & Release | 🔲 Planned |

## License

The license for the code and the AI model weights may differ. Before distributing a public release, review all dependencies, model weights, and their respective usage terms.
