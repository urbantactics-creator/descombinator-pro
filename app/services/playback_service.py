"""Playback service for audio playback."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from loguru import logger
from PySide6.QtCore import QObject, QUrl, Signal, Slot
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer


class PlaybackState(Enum):
    """Playback states."""

    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class PlaybackService(QObject):
    """Service for audio playback using Qt Multimedia."""

    # Signals
    state_changed = Signal(PlaybackState)
    position_changed = Signal(int)  # Position in milliseconds
    duration_changed = Signal(int)  # Duration in milliseconds
    error_occurred = Signal(str)  # Error message

    def __init__(self) -> None:
        super().__init__()
        self._setup_player()
        self._current_file: Path | None = None

    def _setup_player(self) -> None:
        """Initialize the media player and audio output."""
        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)

        # Connect signals
        self._player.playbackStateChanged.connect(self._on_playback_state_changed)
        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.errorOccurred.connect(self._on_error_occurred)

    @Slot()
    def _on_playback_state_changed(self, state) -> None:
        """Handle playback state changes."""
        state_map = {
            QMediaPlayer.PlaybackState.PlayingState: PlaybackState.PLAYING,
            QMediaPlayer.PlaybackState.PausedState: PlaybackState.PAUSED,
            QMediaPlayer.PlaybackState.StoppedState: PlaybackState.STOPPED,
        }
        new_state = state_map.get(state, PlaybackState.STOPPED)
        self.state_changed.emit(new_state)

    @Slot(int)
    def _on_position_changed(self, position: int) -> None:
        """Handle position changes."""
        self.position_changed.emit(position)

    @Slot(int)
    def _on_duration_changed(self, duration: int) -> None:
        """Handle duration changes."""
        self.duration_changed.emit(duration)

    @Slot(str, str)
    def _on_error_occurred(self, error: str, error_string: str) -> None:
        """Handle errors."""
        logger.error(f"Playback error: {error} - {error_string}")
        self.error_occurred.emit(f"{error}: {error_string}")

    async def load_file(self, file_path: Path) -> bool:
        """Load an audio file for playback.

        Args:
            file_path: Path to the audio file

        Returns:
            True if file was loaded successfully, False otherwise
        """
        try:
            self._current_file = file_path
            url = QUrl.fromLocalFile(str(file_path))
            self._player.setSource(url)

            # Wait for the media to load
            # In a real implementation, we might want to wait for the loaded signal
            # For now, we'll return True and let the signals handle updates
            logger.info(f"Loaded audio file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load audio file {file_path}: {e}")
            self.error_occurred.emit(f"Failed to load file: {e}")
            return False

    def play(self) -> None:
        """Start or resume playback."""
        if self._player.source().isEmpty():
            logger.warning("No media loaded for playback")
            return
        self._player.play()

    def pause(self) -> None:
        """Pause playback."""
        self._player.pause()

    def stop(self) -> None:
        """Stop playback."""
        self._player.stop()

    def set_position(self, position_ms: int) -> None:
        """Set playback position.

        Args:
            position_ms: Position in milliseconds
        """
        self._player.setPosition(position_ms)

    def set_volume(self, volume: float) -> None:
        """Set playback volume.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self._audio_output.setVolume(volume)

    def get_state(self) -> PlaybackState:
        """Get current playback state."""
        state_map = {
            QMediaPlayer.PlaybackState.PlayingState: PlaybackState.PLAYING,
            QMediaPlayer.PlaybackState.PausedState: PlaybackState.PAUSED,
            QMediaPlayer.PlaybackState.StoppedState: PlaybackState.STOPPED,
        }
        return state_map.get(self._player.playbackState(), PlaybackState.STOPPED)

    def get_position(self) -> int:
        """Get current playback position in milliseconds."""
        return self._player.position()

    def get_duration(self) -> int:
        """Get media duration in milliseconds."""
        return self._player.duration()

    def is_available(self) -> bool:
        """Check if media playback is available."""
        return self._player.isAvailable()
