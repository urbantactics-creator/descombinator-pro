# Descombinator Pro

Desktop application that separates a song into two AI-powered tracks — **vocals** and **instrumental** — entirely on-device. No files are uploaded to the internet.

## Features

- **High-quality separation** powered by Demucs and Open-Unmix
- **Modern, minimal UI** built with PySide6
- **Fast local processing** with PyTorch acceleration
- **Cross-platform** support (Linux, macOS, Windows)
- **Modular, production-ready** codebase

## Project Status

| Milestone | Status |
| ----------- | -------- |
| Vocal ↔ Instrumental separation | 🚧 In Development |
| Multi-instrument separation | 🔲 Planned |
| Performance optimization | 🔲 Planned |
| Distributable packaging | 🔲 Planned |

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

1. Load audio file
2. Separate vocals and instrumental
3. Play both tracks
4. Export results
5. Performance optimization
6. Packaging for distribution

## License

The license for the code and the AI model weights may differ. Before distributing a public release, review all dependencies, model weights, and their respective usage terms.
