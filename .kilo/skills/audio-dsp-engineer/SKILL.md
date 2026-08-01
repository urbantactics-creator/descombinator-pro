---
name: audio-dsp-engineer
description: >-
  Digital signal processing, audio I/O, resampling, format conversion, and
  audio analysis for the Descombinator Pro engine.
license: MIT
metadata:
  category: dsp
  project: descombinator-pro
---

# Audio DSP Engineer

## Responsibilities

- Implement audio loading, resampling, and format conversion in `engine/audio/`
- Design DSP pipelines for preprocessing and postprocessing
- Handle various audio formats (MP3, WAV, FLAC, M4A, OGG)
- Implement audio analysis (spectral analysis, peak detection)
- Optimize DSP operations for performance

## Audio I/O Stack

| Library | Purpose |
|---------|---------|
| `librosa` | Audio loading and resampling |
| `soundfile` | WAV/FLAC read/write |
| `audioread` | Multi-format decoding |
| `resampy` | High-quality resampling |
| `mutagen` | Metadata reading/writing |

## Key Operations

### Loading

```python
import librosa

def load_audio(path: Path, sr: int = 44100) -> np.ndarray:
    audio, sample_rate = librosa.load(path, sr=sr, mono=True)
    return audio
```

### Resampling

- Use `resampy` with `sinc_best` quality for high-fidelity resampling
- Target sample rate: 44100 Hz (Demucs native)
- Handle sample rate conversion efficiently

### Format Conversion

- Convert all inputs to WAV (16-bit PCM) for processing
- Preserve original metadata when exporting
- Support batch format conversion

## DSP Pipeline

```
Input Audio → Resample → Normalize → [Model] → Denoise → Export
```

### Preprocessing

- DC offset removal
- Peak normalization to -1 dBFS
- Optional noise reduction (spectral gating)

### Postprocessing

- Artifact reduction (windowing, crossfading)
- Dynamic range compression (optional)
- Peak limiting to prevent clipping
