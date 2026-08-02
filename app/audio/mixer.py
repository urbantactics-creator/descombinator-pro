"""In-memory audio mixer driving a QAudioSink.

The mixer exposes a :class:`QIODevice` that a :class:`QAudioSink` pulls
audio from. Tracks are numpy arrays mixed sample-accurately into one
continuous stream, providing synchronized, gapless multi-track playback
without temporary files. ``readData`` runs on the audio thread and never
emits Qt signals; all shared state is protected by a ``QMutex``. A 100 ms
GUI-thread ``QTimer`` emits position/state signals and handles end-of-stream.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

import numpy as np
from loguru import logger
from PySide6.QtCore import QIODevice, QMutex, QMutexLocker, QTimer, Signal
from PySide6.QtMultimedia import QAudioFormat, QAudioSink, QMediaDevices


class PlaybackState(StrEnum):
    """Playback state machine states."""

    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    LOADING = "loading"
    ERROR = "error"


@dataclass
class MixerTrack:
    """A single audio track mixed into the output stream.

    Attributes:
        name: Unique track identifier (e.g. stem name).
        data: Float32 mono audio samples (1D). Multi-channel input should
            be reduced to mono before being added to the mixer.
        sample_rate: Sample rate of the track data.
        gain: Per-track volume gain in ``[0.0, 1.0]``.
        muted: When True the track is excluded from the mix.
        enabled: When False the track is inactive (not counted for EOF).
    """

    name: str
    data: np.ndarray
    sample_rate: int
    gain: float = 1.0
    muted: bool = False
    enabled: bool = True


SinkFactory = Callable[[QAudioFormat], QAudioSink]
FormatFactory = Callable[[], QAudioFormat]

_FLOAT32_BYTES = 4
_INT16_BYTES = 2


class AudioMixer(QIODevice):
    """Mixes numpy tracks into a single stream consumed by a QAudioSink.

    The sink is created lazily on the first :meth:`play` call, which keeps
    the constructor safe in headless environments and unit tests. A
    ``sink_factory``/``format_factory`` can be injected for testing.
    """

    SAMPLE_RATE = 44_100
    CHANNELS = 2

    # Signals (emitted from the GUI thread only)
    state_changed = Signal(PlaybackState)
    position_changed = Signal(int)  # Position in milliseconds
    duration_changed = Signal(int)  # Duration in milliseconds
    error_occurred = Signal(str)  # Error message

    def __init__(
        self,
        sink_factory: SinkFactory | None = None,
        format_factory: FormatFactory | None = None,
    ) -> None:
        super().__init__()
        self.open(QIODevice.OpenModeFlag.WriteOnly)
        self._mutex = QMutex()
        self._tracks: dict[str, MixerTrack] = {}
        self._position_frames = 0
        self._eof = False
        self._state = PlaybackState.STOPPED
        self._sink: QAudioSink | None = None
        self._sink_factory = sink_factory
        self._format_factory = format_factory
        self._bytes_per_frame = self.CHANNELS * _FLOAT32_BYTES
        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._on_timer)

    # --- QIODevice interface ---

    def readData(self, maxlen: int) -> bytes:
        """Produce the next chunk of interleaved audio (audio thread)."""
        frames = maxlen // self._bytes_per_frame
        if frames == 0:
            return b""
        out = np.zeros((frames, self.CHANNELS), dtype=np.float32)
        with QMutexLocker(self._mutex):
            pos = self._position_frames
            for track in self._tracks.values():
                if not (track.enabled and not track.muted):
                    continue
                chunk = track.data[pos : pos + frames]
                if len(chunk):
                    out[: len(chunk), 0] += chunk * track.gain
                    out[: len(chunk), 1] += chunk * track.gain
            self._position_frames += frames
            if not self._has_remaining():
                self._eof = True
        clipped = np.clip(out, -1.0, 1.0)
        if self._bytes_per_frame == self.CHANNELS * _INT16_BYTES:
            return (clipped * 32767).astype(np.int16).tobytes()
        return clipped.astype(np.float32).tobytes()

    def writeData(self, data: bytes) -> int:
        """Write is unsupported; the mixer is a pull-only source."""
        return 0

    # --- Public API ---

    def set_tracks(self, tracks: list[MixerTrack]) -> None:
        """Replace all tracks and reset the stream position."""
        with QMutexLocker(self._mutex):
            self._tracks = {track.name: track for track in tracks}
            self._position_frames = 0
            self._eof = False
        if self._state != PlaybackState.STOPPED:
            self.stop()
        self.duration_changed.emit(self.duration_ms())

    def set_track_gain(self, name: str, gain: float) -> None:
        """Set the per-track gain, clamped to ``[0.0, 1.0]``."""
        with QMutexLocker(self._mutex):
            track = self._tracks.get(name)
            if track is not None:
                track.gain = max(0.0, min(1.0, gain))

    def set_track_muted(self, name: str, muted: bool) -> None:
        """Set the mute flag for a track."""
        with QMutexLocker(self._mutex):
            track = self._tracks.get(name)
            if track is not None:
                track.muted = muted

    def set_active(self, names: list[str]) -> None:
        """Enable only the given tracks and reset the stream position."""
        active = set(names)
        with QMutexLocker(self._mutex):
            for track in self._tracks.values():
                track.enabled = track.name in active
            self._position_frames = 0
            self._eof = False
        if self._state != PlaybackState.STOPPED:
            self.stop()
        self.duration_changed.emit(self.duration_ms())

    def play(self) -> None:
        """Start or resume playback, creating the sink if needed."""
        if not self.has_tracks:
            logger.warning("No tracks loaded for playback")
            return
        if self._sink is None and not self._ensure_sink():
            return
        assert self._sink is not None
        if self._state == PlaybackState.PAUSED:
            self._sink.resume()
        else:
            with QMutexLocker(self._mutex):
                if self._position_frames >= self._total_frames():
                    self._position_frames = 0
            self._sink.start(self)
        self._set_state(PlaybackState.PLAYING)
        self._timer.start()

    def pause(self) -> None:
        """Suspend playback preserving the sink buffer."""
        if self._sink is None or self._state != PlaybackState.PLAYING:
            return
        self._sink.suspend()
        self._set_state(PlaybackState.PAUSED)

    def stop(self) -> None:
        """Stop playback and reset the stream position to zero."""
        self._timer.stop()
        if self._sink is not None:
            self._sink.stop()
        with QMutexLocker(self._mutex):
            self._eof = False
            self._position_frames = 0
        self._set_state(PlaybackState.STOPPED)

    def seek_ms(self, ms: int) -> None:
        """Seek to ``ms`` milliseconds, discarding the sink buffer."""
        with QMutexLocker(self._mutex):
            self._position_frames = max(0, ms * self.SAMPLE_RATE // 1000)
            self._eof = False
        if self._sink is not None:
            self._sink.reset()
        self.position_changed.emit(self.position_ms())

    def set_master_volume(self, volume: float) -> None:
        """Set the master output volume, clamped to ``[0.0, 1.0]``."""
        if self._sink is not None:
            self._sink.setVolume(max(0.0, min(1.0, volume)))

    def position_ms(self) -> int:
        """Current stream position in milliseconds."""
        with QMutexLocker(self._mutex):
            return self._position_frames * 1000 // self.SAMPLE_RATE

    def duration_ms(self) -> int:
        """Stream duration in milliseconds (max over all tracks)."""
        with QMutexLocker(self._mutex):
            frames = max(
                (len(track.data) for track in self._tracks.values()), default=0
            )
        return frames * 1000 // self.SAMPLE_RATE

    @property
    def state(self) -> PlaybackState:
        """Current playback state."""
        return self._state

    @property
    def has_tracks(self) -> bool:
        """True when at least one track is loaded."""
        with QMutexLocker(self._mutex):
            return bool(self._tracks)

    def track_names(self) -> list[str]:
        """Names of all loaded tracks in insertion order."""
        with QMutexLocker(self._mutex):
            return list(self._tracks)

    def track_gains(self) -> dict[str, float]:
        """Mapping of track name to current gain."""
        with QMutexLocker(self._mutex):
            return {name: track.gain for name, track in self._tracks.items()}

    def track_muted_map(self) -> dict[str, bool]:
        """Mapping of track name to current mute flag."""
        with QMutexLocker(self._mutex):
            return {name: track.muted for name, track in self._tracks.items()}

    def active_stems(self) -> list[str]:
        """Names of enabled (active) tracks."""
        with QMutexLocker(self._mutex):
            return [name for name, t in self._tracks.items() if t.enabled]

    # --- Internals ---

    def _ensure_sink(self) -> bool:
        """Create and start the audio sink, falling back to Int16."""
        device = QMediaDevices.defaultAudioOutput()
        if device.isNull():
            message = "No audio output device available"
            logger.error(message)
            self.error_occurred.emit(message)
            self._set_state(PlaybackState.ERROR)
            return False

        if self._format_factory is not None:
            fmt = self._format_factory()
        else:
            fmt = self._build_format()
            if not device.isFormatSupported(fmt):
                fmt = self._build_format(QAudioFormat.SampleFormat.Int16)

        self._bytes_per_frame = fmt.bytesPerFrame()
        if self._sink_factory is not None:
            self._sink = self._sink_factory(fmt)
        else:
            self._sink = QAudioSink(device, fmt)
        self._sink.setVolume(1.0)
        self._sink.start(self)
        return True

    def _build_format(
        self,
        sample_format: QAudioFormat.SampleFormat = QAudioFormat.SampleFormat.Float,
    ) -> QAudioFormat:
        fmt = QAudioFormat()
        fmt.setSampleRate(self.SAMPLE_RATE)
        fmt.setChannelCount(self.CHANNELS)
        fmt.setSampleFormat(sample_format)
        return fmt

    def _total_frames(self) -> int:
        """Number of frames of the longest track."""
        return max((len(track.data) for track in self._tracks.values()), default=0)

    def _has_remaining(self) -> bool:
        """True when any enabled track still has data to play."""
        return any(
            track.enabled and len(track.data) > self._position_frames
            for track in self._tracks.values()
        )

    def _set_state(self, state: PlaybackState) -> None:
        """Update state and emit ``state_changed`` on transition."""
        if self._state != state:
            self._state = state
            self.state_changed.emit(state)

    def _on_timer(self) -> None:
        """GUI-thread timer: handle EOF and report position."""
        with QMutexLocker(self._mutex):
            eof = self._eof
            position = self._position_frames
        if eof and self._state != PlaybackState.STOPPED:
            self._timer.stop()
            if self._sink is not None:
                self._sink.stop()
            with QMutexLocker(self._mutex):
                self._eof = False
            self._set_state(PlaybackState.STOPPED)
        self.position_changed.emit(position * 1000 // self.SAMPLE_RATE)
