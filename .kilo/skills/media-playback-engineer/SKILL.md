---
name: media-playback-engineer
description: >-
  Audio playback implementation, media controls, streaming, and playback
  state management for the Descombinator Pro application.
license: MIT
metadata:
  category: engineering
  project: descombinator-pro
---

# Media Playback Engineer

## Responsibilities

- Implement audio playback for separated tracks
- Design media controls (play, pause, seek, volume)
- Handle playback state management
- Implement waveform visualization
- Support gapless playback and crossfading

## Playback Stack

| Library | Purpose |
|---------|---------|
| `PySide6.QtMultimedia` | Qt audio playback |
| `sounddevice` | Low-latency audio output |
| `numpy` | Audio buffer manipulation |
| `librosa` | Audio analysis for visualization |

## Playback Architecture

```
app/widgets/          → Playback UI widgets
app/controllers/      → Playback state logic
engine/audio/         → Audio buffer management
```

## Key Components

### Audio Player

```python
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtCore import QUrl

class AudioPlayer:
    def __init__(self):
        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)

    def load(self, file_path: Path):
        self._player.setSource(QUrl.fromLocalFile(str(file_path)))

    def play(self):
        self._player.play()

    def pause(self):
        self._player.pause()

    def set_position(self, position: int):
        self._player.set_position(position)

    def set_volume(self, volume: float):
        self._audio_output.set_volume(volume)
```

### Playback State

| State | Description |
|-------|-------------|
| Stopped | No track loaded or playback ended |
| Playing | Track is currently playing |
| Paused | Playback is paused |
| Loading | Track is being loaded |
| Error | Playback error occurred |

## Media Controls

### Transport Controls

- Play/Pause toggle button
- Stop button
- Seek slider with position indicator
- Time display (current / total)

### Volume Controls

- Volume slider (0-100%)
- Mute toggle
- Separate volume per track

### Track Selection

- Dropdown to select vocals or instrumental
- Visual indication of active track
- Independent playback state per track

## Waveform Visualization

- Render waveform from audio data
- Display playback position
- Support zoom and pan
- Use `pyqtgraph` for real-time rendering
