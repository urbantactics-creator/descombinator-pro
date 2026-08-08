"""Controller for multi-track audio playback with persistence."""

import numpy as np
from PySide6.QtCore import QObject, QTimer, Signal, Slot

from app.services.playback_service import PlaybackService
from app.services.playback_state_store import PlaybackStateStore


class PlaybackController(QObject):
    """Coordinates playback between the UI and the :class:`PlaybackService`.

    Owns the persistence of per-track volumes, mutes, active stems and the
    last loaded file. Volume/mute changes are saved debounced (400 ms);
    active stems and the last file are persisted immediately.
    """

    # Signals for UI updates
    position_changed = Signal(int)  # Position in milliseconds
    duration_changed = Signal(int)  # Duration in milliseconds
    state_changed = Signal(str)  # Playback state value (e.g. "playing")
    master_volume_changed = Signal(float)  # Master volume (0.0-1.0)
    error_occurred = Signal(str)  # Error message
    tracks_changed = Signal(list)  # list[str] of loaded stem names
    track_volume_changed = Signal(str, float)  # name, volume
    track_muted_changed = Signal(str, bool)  # name, muted

    _SAVE_DELAY_MS = 400

    def __init__(
        self,
        service: PlaybackService | None = None,
        store: PlaybackStateStore | None = None,
    ) -> None:
        super().__init__()
        self._service = service if service is not None else PlaybackService()
        self._store = store if store is not None else PlaybackStateStore()
        self._last_file: str | None = None
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(self._SAVE_DELAY_MS)
        self._save_timer.timeout.connect(self._flush_save)
        self._connect_signals()

    def _connect_signals(self) -> None:
        """Bridge playback service signals to controller signals."""
        self._service.state_changed.connect(
            lambda state: self.state_changed.emit(state.value)
        )
        self._service.position_changed.connect(self.position_changed.emit)
        self._service.duration_changed.connect(self.duration_changed.emit)
        self._service.error_occurred.connect(self.error_occurred.emit)

    @Slot()
    def play(self) -> None:
        """Start or resume playback."""
        self._service.play()

    @Slot()
    def pause(self) -> None:
        """Pause playback."""
        self._service.pause()

    @Slot()
    def stop(self) -> None:
        """Stop playback."""
        self._service.stop()

    def set_source(self, audio: np.ndarray, sample_rate: int) -> None:
        """Set the original (pre-separation) audio as the single source."""
        self._service.set_source(audio, sample_rate)

    def set_stems(self, stems: dict[str, np.ndarray]) -> None:
        """Load separated stems and restore persisted per-track state."""
        self._service.set_stems(stems)
        persisted = self._store.load()
        volumes = persisted.get("volumes") or {}
        muted = persisted.get("muted") or {}
        for name in stems:
            self._service.set_track_volume(name, volumes.get(name, 1.0))
            self._service.set_track_muted(name, muted.get(name, False))
        active = persisted.get("active_stems") or list(stems)
        self._service.set_active_stems(active)
        self.tracks_changed.emit(list(stems))

    @Slot(int)
    def set_position(self, position_ms: int) -> None:
        """Seek to the given millisecond position."""
        self._service.seek_ms(position_ms)

    def seek_ms(self, ms: int) -> None:
        """Seek to the given millisecond position."""
        self._service.seek_ms(ms)

    def set_track_volume(self, name: str, volume: float) -> None:
        """Set a per-track volume and schedule a persisted save."""
        self._service.set_track_volume(name, volume)
        self.track_volume_changed.emit(name, volume)
        self._schedule_save()

    def set_track_muted(self, name: str, muted: bool) -> None:
        """Set a per-track mute flag and schedule a persisted save."""
        self._service.set_track_muted(name, muted)
        self.track_muted_changed.emit(name, muted)
        self._schedule_save()

    def set_active_stems(self, names: list[str]) -> None:
        """Set the active stems and persist immediately."""
        self._service.set_active_stems(names)
        self._flush_save()

    def set_master_volume(self, volume: float) -> None:
        """Set the master output volume."""
        self._service.set_master_volume(volume)
        self.master_volume_changed.emit(volume)

    @Slot(float)
    def set_volume(self, volume: float) -> None:
        """Set the master output volume (legacy alias)."""
        self.set_master_volume(volume)

    def record_last_file(self, file_path: str) -> None:
        """Record the last loaded file and persist immediately."""
        self._last_file = file_path
        self._flush_save()

    def reset(self) -> None:
        """Stop playback, clear tracks and persist a clean snapshot."""
        self._service.stop()
        self._service.clear()
        self._save_timer.stop()
        self._flush_save()

    def get_state(self) -> str:
        """Current playback state as a string value."""
        return self._service.get_state().value

    def get_position(self) -> int:
        """Current position in milliseconds."""
        return self._service.get_position()

    def get_duration(self) -> int:
        """Current stream duration in milliseconds."""
        return self._service.get_duration()

    def track_names(self) -> list[str]:
        """Names of all loaded tracks."""
        return self._service.track_names()

    def track_volumes(self) -> dict[str, float]:
        """Mapping of track name to current volume."""
        return self._service.track_volumes()

    def muted_map(self) -> dict[str, bool]:
        """Mapping of track name to current mute flag."""
        return self._service.muted_map()

    def active_stems(self) -> list[str]:
        """Names of enabled stems."""
        return self._service.active_stems()

    def has_stems(self) -> bool:
        """True when separated stems are loaded."""
        return self._service.has_stems()

    def has_media(self) -> bool:
        """True when any audio track is loaded."""
        return self._service.has_tracks()

    # --- Persistence ---

    def _schedule_save(self) -> None:
        """Restart the debounce timer for volume/mute changes."""
        if self._save_timer.isActive():
            self._save_timer.stop()
        self._save_timer.start()

    def _flush_save(self) -> None:
        """Persist the current playback state snapshot."""
        self._store.save(
            volumes=self.track_volumes(),
            muted=self.muted_map(),
            active_stems=self.active_stems(),
            last_file=self._last_file,
        )
