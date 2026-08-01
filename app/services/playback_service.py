"""Playback service orchestrating the in-memory audio mixer."""

from __future__ import annotations

import numpy as np
import resampy
from PySide6.QtCore import QObject, Signal

from app.audio.mixer import AudioMixer, MixerTrack, PlaybackState

__all__ = ["PlaybackState"]


class PlaybackService(QObject):
    """Multi-track playback backed by an in-memory :class:`AudioMixer`.

    Stems are numpy arrays already loaded in memory; the service converts
    them to mono mixer tracks (resampling to 44.1 kHz only when needed) and
    bridges the mixer's signals to its own for the controller layer.
    """

    state_changed = Signal(PlaybackState)
    position_changed = Signal(int)  # Position in milliseconds
    duration_changed = Signal(int)  # Duration in milliseconds
    error_occurred = Signal(str)  # Error message

    def __init__(self, mixer: AudioMixer | None = None) -> None:
        super().__init__()
        self._mixer = mixer if mixer is not None else AudioMixer()
        self._mixer.state_changed.connect(self.state_changed.emit)
        self._mixer.position_changed.connect(self.position_changed.emit)
        self._mixer.duration_changed.connect(self.duration_changed.emit)
        self._mixer.error_occurred.connect(self.error_occurred.emit)

    def set_source(self, audio: np.ndarray, sample_rate: int) -> None:
        """Replace all tracks with a single source track (original audio)."""
        self.state_changed.emit(PlaybackState.LOADING)
        self._mixer.set_tracks(
            [
                MixerTrack(
                    name="source",
                    data=self._as_mono(audio),
                    sample_rate=sample_rate,
                )
            ]
        )
        self.state_changed.emit(PlaybackState.STOPPED)

    def set_stems(
        self, stems: dict[str, np.ndarray], sample_rate: int = 44_100
    ) -> None:
        """Replace all tracks with separated stems (removing ``source``)."""
        tracks: list[MixerTrack] = []
        for name, data in stems.items():
            mono = self._as_mono(data)
            if sample_rate != AudioMixer.SAMPLE_RATE:
                mono = resampy.resample(
                    mono,
                    sample_rate,
                    AudioMixer.SAMPLE_RATE,
                    filter="kaiser_best",
                )
            tracks.append(
                MixerTrack(name=name, data=mono, sample_rate=AudioMixer.SAMPLE_RATE)
            )
        self._mixer.set_tracks(tracks)

    def clear(self) -> None:
        """Remove all tracks and reset the mixer."""
        self._mixer.set_tracks([])

    def play(self) -> None:
        """Start or resume playback."""
        self._mixer.play()

    def pause(self) -> None:
        """Pause playback."""
        self._mixer.pause()

    def stop(self) -> None:
        """Stop playback."""
        self._mixer.stop()

    def seek_ms(self, ms: int) -> None:
        """Seek to the given millisecond position."""
        self._mixer.seek_ms(ms)

    def set_position(self, ms: int) -> None:
        """Alias for :meth:`seek_ms` kept for backwards compatibility."""
        self.seek_ms(ms)

    def set_master_volume(self, volume: float) -> None:
        """Set the master output volume (0.0-1.0)."""
        self._mixer.set_master_volume(volume)

    def set_volume(self, volume: float) -> None:
        """Alias for :meth:`set_master_volume`."""
        self.set_master_volume(volume)

    def set_track_volume(self, name: str, volume: float) -> None:
        """Set the volume of a single track (0.0-1.0)."""
        self._mixer.set_track_gain(name, volume)

    def set_track_muted(self, name: str, muted: bool) -> None:
        """Mute or unmute a single track."""
        self._mixer.set_track_muted(name, muted)

    def set_active_stems(self, names: list[str]) -> None:
        """Enable only the given stems in the mix."""
        self._mixer.set_active(names)

    def get_state(self) -> PlaybackState:
        """Current playback state."""
        return self._mixer.state

    def get_position(self) -> int:
        """Current position in milliseconds."""
        return self._mixer.position_ms()

    def get_duration(self) -> int:
        """Current stream duration in milliseconds."""
        return self._mixer.duration_ms()

    def has_tracks(self) -> bool:
        """True when any track is loaded."""
        return self._mixer.has_tracks

    def track_names(self) -> list[str]:
        """Names of all loaded tracks."""
        return self._mixer.track_names()

    def track_volumes(self) -> dict[str, float]:
        """Mapping of track name to current volume."""
        return self._mixer.track_gains()

    def muted_map(self) -> dict[str, bool]:
        """Mapping of track name to current mute flag."""
        return self._mixer.track_muted_map()

    def active_stems(self) -> list[str]:
        """Names of enabled stems."""
        return self._mixer.active_stems()

    def has_stems(self) -> bool:
        """True when separated stems are loaded (beyond the raw source)."""
        names = self._mixer.track_names()
        return bool(names) and names != ["source"]

    @staticmethod
    def _as_mono(audio: np.ndarray) -> np.ndarray:
        """Reduce multi-channel audio to mono, reusing 1D float32 buffers."""
        mono = np.mean(audio, axis=0) if audio.ndim == 2 else audio
        # numpy stubs type astype() as Any; the cast is verified by tests.
        return mono.astype(np.float32, copy=False)  # type: ignore[no-any-return]
