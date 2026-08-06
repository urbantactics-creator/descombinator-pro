# Tech Stack

The technologies and libraries that power Descombinator Pro.

## Core Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Programming language | 3.12+ |
| **PyTorch** | ML framework | >=2.13.0 |
| **PySide6** | Desktop UI framework | >=6.11.1 |
| **Demucs** | Music source separation | >=4.1.0 |
| **Open-Unmix** | Alternative separation model | >=1.3.0 |

## Audio Processing

| Library | Purpose | Version |
|---------|---------|---------|
| **librosa** | Audio analysis and feature extraction | >=0.11.0 |
| **soundfile** | Audio file I/O | >=0.14.0 |
| **audioread** | Audio decoding backend | >=3.1.0 |
| **resampy** | Audio resampling | >=0.4.3 |
| **mutagen** | Audio metadata | >=1.48.1 |
| **scipy** | Signal processing | >=1.18.0 |
| **numpy** | Numerical computing | >=2.4.6 |

## UI and Visualization

| Library | Purpose | Version |
|---------|---------|---------|
| **PySide6** | Qt-based desktop UI | >=6.11.1 |
| **pyqtgraph** | Real-time plotting and waveforms | >=0.14.0 |

## Async and Utilities

| Library | Purpose | Version |
|---------|---------|---------|
| **aiofiles** | Async file I/O | >=25.1.0 |
| **pydantic** | Data validation and settings | >=2.13.4 |
| **loguru** | Logging | >=0.7.3 |
| **python-dotenv** | Environment variables | >=1.2.2 |
| **pyyaml** | YAML configuration | >=6.0.3 |
| **tqdm** | Progress bars | >=4.70.0 |
| **rich** | Terminal formatting | >=15.0.0 |
| **psutil** | System monitoring | >=7.2.2 |

## ML Acceleration

| Library | Purpose | Version |
|---------|---------|---------|
| **torchaudio** | Audio processing for PyTorch | >=2.11.0 |
| **onnxruntime** | ONNX model inference | >=1.28.0 |

## Development and CI

| Tool | Purpose | Version |
|------|---------|---------|
| **pytest** | Testing framework | >=9.1.1 |
| **pytest-qt** | Qt testing | >=4.5.0 |
| **pytest-asyncio** | Async testing | >=1.4.0 |
| **mypy** | Static type checking | >=2.3.0 |
| **ruff** | Linting and formatting | >=0.16.1 |
| **pre-commit** | Git hooks | >=4.6.0 |
| **pyinstaller** | Packaging | >=6.21.0 |

## Documentation

| Tool | Purpose | Version |
|------|---------|---------|
| **MkDocs** | Static site generator | >=1.6.0 |
| **Material for MkDocs** | Theme | >=9.5.0 |
| **mkdocstrings** | API documentation from docstrings | >=0.25.0 |

## Why These Choices?

- **Python 3.12+:** Modern type hints, performance improvements, async features
- **PyTorch:** Industry standard for ML, excellent CUDA support
- **PySide6:** Official Qt bindings for Python, mature and well-documented
- **Demucs:** State-of-the-art music separation, actively maintained by Meta
- **librosa:** De facto standard for audio analysis in Python
- **pydantic:** Type-safe data validation, settings management
- **loguru:** Better logging than the standard library
