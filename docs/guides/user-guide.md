# User Guide

This guide covers installation, usage, and feature walkthroughs for Descombinator Pro.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Separating Audio](#separating-audio)
- [Playback Controls](#playback-controls)
- [Exporting Results](#exporting-results)
- [Settings](#settings)
- [Performance](#performance)

## Installation

### Prerequisites

- Python 3.12+
- System dependencies:
  - **Linux:** `libegl1 libgl1 libopengl0 libpulse0 ffmpeg`
  - **macOS:** FFmpeg (`brew install ffmpeg`)
  - **Windows:** FFmpeg (download from [ffmpeg.org](https://ffmpeg.org/download.html))

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd descombinator

# Create and activate the virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install .[dev]
```

> **Tip:** If you have [direnv](https://direnv.net/) installed, the `.envrc` file will auto-activate the venv.

### Distributable Builds

Prebuilt installers are built with PyInstaller — see `descombinator.spec` and `scripts/build/` (AppImage on Linux, Inno Setup `.exe` on Windows, `.app` bundle on macOS).

## Quick Start

1. Launch the application:
   ```bash
   python main.py
   ```

2. Drag and drop an audio file onto the window, or click the file selection area.

3. Click **Separate** to start the AI-powered separation process.

4. Once complete, use the playback controls to listen to the separated tracks.

5. Click **Export** to save the separated tracks to disk.

## Separating Audio

### Supported Formats

- MP3, WAV, FLAC, M4A, OGG

### Separation Models

| Model | Description |
|-------|-------------|
| `htdemucs_ft` | Primary model — high-quality Demucs separation |
| `mdx_extra` | Alternative model — high-quality Demucs with different training |
| `umxhq` | Open-Unmix model — alternative separation approach |

Select the model in **Settings** → **Model**.

### Process

1. Load an audio file (drag-and-drop or file dialog)
   - **Enhanced drag-and-drop feedback:** The drop zone changes color and displays helpful hints when dragging files over it
   - Green background indicates a supported audio file
   - Red background indicates an unsupported file format
2. The waveform is displayed for both the original and separated tracks
3. Click **Separate** to start processing
4. A progress dialog shows the status and estimated time remaining
   - **Animated progress bar** with smooth transitions
   - **Status bar progress indicator** with color-changing background (green to red as processing advances)
   - **Progress icon** in the status bar for visual feedback
5. You can cancel the separation at any time

## Playback Controls

### Multi-Track Playback

- **Vocals** and **Instrumental** tracks play in sync
- Each track has independent **volume** and **mute** controls
- **Gapless playback** ensures seamless looping

### Controls

| Control | Action |
|---------|--------|
| Play/Pause | Start or pause playback |
| Stop | Stop playback and reset position |
| Seek slider | Drag to seek to a position |
| Volume slider | Adjust track volume |
| Mute toggle | Mute/unmute track |

### Waveform Visualization

- The waveform view shows the audio waveform with a playback position indicator
- The position line updates in real-time during playback
- Click on the waveform to seek to that position

## Exporting Results

### Supported Formats

| Format | Quality | Use Case |
|--------|---------|----------|
| WAV | Lossless, 16/24-bit PCM | Professional use |
| FLAC | Lossless, compression level 5 | Archiving |
| MP3 | Lossy, 192–320 kbps VBR | Sharing |
| M4A | Lossy, AAC encoding | Apple ecosystem |

### Export Options

- **Format:** Select the output format
- **Sample rate:** 8000–192000 Hz (default: 44100)
- **Bit depth:** 8–32 bits (default: 16, WAV/FLAC only)
- **Bitrate:** 32–320 kbps (default: 192, MP3/M4A only)
- **Normalize:** Apply peak normalization to -1 dBFS
- **Fade in/out:** Apply fade-in and fade-out effects (0–10 seconds)
- **Metadata:** Embed title, artist, album, and artwork

### Batch Export

All separated stems are exported together. The output directory will contain:

```
output/
├── vocals.wav
├── instrumental.wav
├── drums.wav
├── bass.wav
└── other.wav
```

## Settings

### Model Selection

Choose the separation model:
- `htdemucs_ft` (default) — Best overall quality
- `mdx_extra` — Alternative high-quality model
- `umxhq` — Open-Unmix model

### Output Format

Set the default export format:
- WAV (default)
- FLAC
- MP3
- M4A

### Performance

- **Max workers:** Number of parallel processing workers (default: CPU count)
- **GPU acceleration:** Automatically used if CUDA is available

### Theme

- **Light** — Light theme
- **Dark** (default) — Dark theme

## UI Enhancements

### Drag-and-Drop Feedback

The file drop zone provides enhanced visual feedback:
- **Idle state:** Dashed gray border with "Drag & drop an audio file here"
- **Valid file dragged over:** Solid green border, light green background, "Drop to load audio file"
- **Invalid file dragged over:** Solid red border, light red background, "Unsupported format"
- Smooth animated transitions between states

### Processing Animations

During audio separation, the UI provides multiple visual indicators:
- **Progress dialog:** Animated progress bar with smooth easing
- **Status bar progress:** Color-changing background (green → yellow → red) based on completion percentage
- **Status bar icon:** Animated hourglass icon during processing
- **Screen transition:** Subtle fade effect when separation starts/completes

### Waveform Visualization

- The waveform view shows the audio waveform with a playback position indicator
- The position line updates in real-time during playback
- Click on the waveform to seek to that position
- Theme-aware colors (adapts to light/dark mode)

## Performance

### Startup Time

The application uses lazy imports to achieve fast startup (~1 second). The ML stack (PyTorch, Demucs, etc.) is only loaded when a separation is started.

### Separation Time

| Hardware | 3-minute song |
|----------|---------------|
| CPU (8 cores) | ~15-30 seconds |
| GPU (CUDA) | ~5-10 seconds |

### Memory Usage

Peak memory usage is typically < 500 MB for a 3-minute song. The application uses chunked processing to limit memory usage.

### Benchmark Results

CI runs a benchmark regression gate on every PR. Key results:

| Benchmark | CI Median | Target |
|-----------|-----------|--------|
| Startup import | ~1.09 s | < 3 s |
| Playback interactions | < 0.1 ms | < 100 ms |
| Waveform decimation | ~2.1 ms | < 100 ms |
| Memory peak | 133 MB | < 4 GB |

### Thermal Monitoring

The status bar shows CPU/GPU temperature when sensors are available (Linux `coretemp`/`k10temp`; NVIDIA via `nvidia-smi`). macOS/Windows may not report temperatures and the app runs normally. On sustained heat the app reduces CPU threads (HOT) and pauses separation (CRITICAL).

See `roadmap.md` (Phases 8-9) for full details.
