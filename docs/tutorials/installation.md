# Installation

Get Descombinator Pro running on your machine in minutes.

## Prerequisites

- **Python 3.12 or later**
- **FFmpeg** for audio decoding/encoding
- **Git** (if installing from source)

### System Dependencies

| Platform | Command |
|----------|---------|
| **Ubuntu/Debian** | `sudo apt-get install -y libegl1 libgl1 libopengl0 libpulse0 ffmpeg` |
| **macOS** | `brew install ffmpeg` |
| **Windows** | Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH |

## Install from Source

```bash
# Clone the repository
git clone https://github.com/descombinator/descombinator.git
cd descombinator

# Create and activate the virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -e ".[dev]"
```

> **Tip:** If you have [direnv](https://direnv.net/) installed, the `.envrc` file will auto-activate the virtual environment.

## Install with pip

```bash
pip install descombinator
```

## Verify Installation

```bash
python -c "import descombinator; print(descombinator.__version__)"
```

## Next Steps

- [Quick Start](quick-start.md) — Your first separation in 3 steps
- [User Guide](https://descombinator.github.io/descombinator/guides/user-guide/) — Full feature walkthrough
