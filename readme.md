# Descombinator Pro

Desktop application that separates a song into two AI-powered tracks — **vocals** and **instrumental** — entirely on-device. No files are uploaded to the internet.

## Project Status

| Milestone | Status |
| ----------- | -------- |
| Vocal ↔ Instrumental separation | ✅ Complete |
| Multi-instrument separation | 🔲 Planned |
| Playback & waveform visualization | ✅ Complete |
| Performance optimization | ✅ Complete |
| Distributable packaging | 🔲 Planned |

## Features

- **High-quality separation** powered by Demucs and Open-Unmix
- **Modern, minimal UI** built with PySide6
- **Fast local processing** with PyTorch acceleration
- **On-device privacy** — no files uploaded to the internet
- **Synchronized multi-track playback** with per-track volume/mute, seek, and gapless mixing
- **Waveform visualization** with playback position tracking
- **Performance-tested** — 16 benchmark gates enforced in CI (regression gate fails on > 20 % median drift)
- **Cross-platform** support (Linux, macOS, Windows)
- **Modular, production-ready** codebase

## Tech Stack

| Category | Technology |
| ---------- | ------------ |
| Language | Python 3.12+ |
| GUI Framework | PySide6 |
| ML Backend | PyTorch, TorchAudio |
| Separation | Demucs, Open-Unmix |
| Audio I/O | Librosa, SoundFile, Resampy |
| Metadata | Mutagen |
| Visualization | PyQtGraph |
| Async I/O | aiofiles |
| Logging | Loguru |
| Testing | pytest, pytest-qt |
| Packaging | PyInstaller |

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
│   └── export/       # Result export and file writing
├── tests/            # Unit and integration tests
├── docs/             # Documentation
├── assets/           # Project assets
├── .venv/            # Virtual environment (auto-activated)
├── main.py           # Application entry point
├── requirements.txt  # Python dependencies
├── pyproject.toml    # Project configuration
├── .envrc          # direnv auto-activation
└── activate.sh     # Manual venv activation script
```

## Installation

### Prerequisites

- Python 3.12+
- pip

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
```

> **Tip:** If you have [direnv](https://direnv.net/) installed, the `.envrc` file will auto-activate the venv when you enter the project directory.

## Usage

```bash
# With venv activated
python main.py
```

## Development

### Running Tests

```bash
pytest tests/
```

### Building a Distributable

```bash
pyinstaller --onefile main.py
```

## Roadmap

1. ✅ Load audio file
2. ✅ Separate vocals and instrumental
3. ✅ Play both tracks
4. ✅ Export results
5. ✅ Performance optimization (benchmarks, baselines, CI regression gate)
6. 🔲 Packaging for distribution
7. 🔲 Testing & QA hardening (coverage gates)
8. 🔲 Documentation & release

## Performance

Phase 8 (Performance Optimization) is delivered. CI runs a benchmark regression gate:

```bash
# Run the benchmark suite (non-slow gates)
pytest benchmarks/ -m "not slow" --benchmark-only

# Check regressions against committed baselines
python -m scripts.bench.check_regressions --baseline benchmarks/baselines.json --result bench_results.json
```

Key results (real CI medians): startup import ~1.09 s (target < 3 s), playback interactions < 0.1 ms, waveform decimation ~2.1 ms, memory peak 133 MB (target < 4 GB). See `roadmap.md` (Phase 8) and `docs/development/performance/` for details.

## License

The license for the code and the AI model weights may differ. Before distributing a public release, review all dependencies, model weights, and their respective usage terms.
