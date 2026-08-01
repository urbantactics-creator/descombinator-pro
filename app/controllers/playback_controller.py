"""Controller for audio playback functionality."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from app.services.playback_service import PlaybackService


class PlaybackController(QObject):
    """Controller for managing audio playback."""

    # Signals for UI updates
    position_changed = Signal(int)  # Position in milliseconds
    duration_changed = Signal(int)  # Duration in milliseconds
    state_changed = Signal(str)  # Playback state (playing, paused, stopped)
    volume_changed = Signal(float)  # Volume level (0.0-1.0)
    error_occurred = Signal(str)  # Error message

    def __init__(self) -> None:
        super().__init__()
        self._playback_service = PlaybackService()
        self._connect_signals()

    def _connect_signals(self) -> None:
        """Connect playback service signals to controller signals."""
        self._playback_service.state_changed.connect(
            lambda state: self.state_changed.emit(state.value)
        )
        self._playback_service.position_changed.connect(self.position_changed.emit)
        self._playback_service.duration_changed.connect(self.duration_changed.emit)
        self._playback_service.error_occurred.connect(self.error_occurred.emit)

    @Slot()
    def play(self) -> None:
        """Start or resume playback."""
        self._playback_service.play()

    @Slot()
    def pause(self) -> None:
        """Pause playback."""
        self._playback_service.pause()

    @Slot()
    def stop(self) -> None:
        """Stop playback."""
        self._playback_service.stop()

    @Slot(str)
    def load_file(self, file_path: str) -> None:
        """Load an audio file for playback.

        Args:
            file_path: Path to the audio file
        """
        path = Path(file_path)
        self._playback_service.load_file(path)

    @Slot(int)
    def set_position(self, position_ms: int) -> None:
        """Set the playback position.

        Args:
            position_ms: Position in milliseconds
        """
        self._playback_service.set_position(position_ms)

    @Slot(float)
    def set_volume(self, volume: float) -> None:
        """Set the playback volume.

        Args:
            volume: Volume level (0.0-1.0)
        """
        self._playback_service.set_volume(volume)

    def get_state(self) -> str:
        """Get current playback state as string."""
        return self._playback_service.get_state().value

    def get_position(self) -> int:
        """Get current playback position in milliseconds."""
        return self._playback_service.get_position()

    def get_duration(self) -> int:
        """Get media duration in milliseconds."""
        return self._playback_service.get_duration()
