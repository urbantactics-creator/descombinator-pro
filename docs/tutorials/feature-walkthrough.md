# Feature Walkthrough

A guided tour of Descombinator Pro's main features.

## Audio Separation

The core feature. Load any audio file and separate it into stems.

### Supported Models

| Model | Description | Best For |
|-------|-------------|----------|
| `htdemucs_ft` | Primary Demucs model | Best overall quality |
| `mdx_extra` | Alternative Demucs model | Different training approach |
| `umxhq` | Open-Unmix model | Alternative separation approach |

Select the model in **Settings** → **Model**.

### Process

1. Load an audio file (drag-and-drop or file dialog)
2. The waveform is displayed for both the original and separated tracks
3. Click **Separate** to start processing
4. A progress dialog shows the status and estimated time remaining
5. You can cancel the separation at any time

## Playback

### Multi-Track Playback

- **Vocals** and **Instrumental** tracks play in sync
- Each track has independent **volume** and **mute** controls
- **Gapless playback** ensures seamless looping

### Waveform Visualization

- The waveform view shows the audio waveform with a playback position indicator
- The position line updates in real-time during playback
- Click on the waveform to seek to that position

## Export

Export separated tracks in multiple formats with full control over quality and metadata.

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

### Thermal Monitoring

The status bar shows CPU/GPU temperature when sensors are available. On sustained heat the app reduces CPU threads (HOT) and pauses separation (CRITICAL).
