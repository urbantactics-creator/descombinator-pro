"""Playback controls widget with seek slider and time display."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QStyle,
    QVBoxLayout,
    QWidget,
)


class PlaybackControls(QWidget):
    """Media transport controls: play/pause/stop, seek, time and volume.

    The seek slider supports live seeking: while the user drags, programmatic
    position updates are skipped and ``position_changed`` is emitted from
    ``sliderMoved`` plus once more on release.
    """

    play_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()
    position_changed = Signal(int)  # Position in milliseconds
    volume_changed = Signal(float)  # Volume as 0.0-1.0

    def __init__(self) -> None:
        super().__init__()
        self._duration_ms = 0
        self._position_ms = 0
        self._dragging = False
        self._updating = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Transport controls
        transport_layout = QHBoxLayout()

        self._play_button = QPushButton()
        self._play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self._play_button.clicked.connect(self._on_play_clicked)
        transport_layout.addWidget(self._play_button)

        self._pause_button = QPushButton()
        self._pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self._pause_button.clicked.connect(self._on_pause_clicked)
        transport_layout.addWidget(self._pause_button)

        self._stop_button = QPushButton()
        self._stop_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self._stop_button.clicked.connect(self._on_stop_clicked)
        transport_layout.addWidget(self._stop_button)

        transport_layout.addStretch()
        layout.addLayout(transport_layout)

        # Seek slider with time display
        position_layout = QHBoxLayout()

        self._position_label = QLabel("0:00")
        position_layout.addWidget(self._position_label)

        self._position_slider = QSlider(Qt.Horizontal)
        self._position_slider.setRange(0, 0)
        self._position_slider.setEnabled(False)
        self._position_slider.sliderPressed.connect(self._on_slider_pressed)
        self._position_slider.sliderMoved.connect(self._on_position_slider_moved)
        self._position_slider.sliderReleased.connect(self._on_slider_released)
        position_layout.addWidget(self._position_slider)

        self._duration_label = QLabel("0:00")
        position_layout.addWidget(self._duration_label)
        layout.addLayout(position_layout)

        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))

        self._volume_slider = QSlider(Qt.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setValue(70)  # Default 70%
        self._volume_slider.valueChanged.connect(self._on_volume_changed)
        volume_layout.addWidget(self._volume_slider)

        self._volume_label = QLabel("70%")
        volume_layout.addWidget(self._volume_label)
        layout.addLayout(volume_layout)

    # --- Internal handlers ---

    def _on_play_clicked(self) -> None:
        """Emit play_clicked when the play button is pressed."""
        self.play_clicked.emit()

    def _on_pause_clicked(self) -> None:
        """Emit pause_clicked when the pause button is pressed."""
        self.pause_clicked.emit()

    def _on_stop_clicked(self) -> None:
        """Emit stop_clicked when the stop button is pressed."""
        self.stop_clicked.emit()

    def _on_slider_pressed(self) -> None:
        """Mark the seek slider as being dragged."""
        self._dragging = True
        self._last_seek_position: int | None = None

    def _on_position_slider_moved(self, position: int) -> None:
        """Update position while the user drags the seek slider."""
        if self._dragging:
            self.set_current_time(position)
            self._last_seek_position = position
            self.position_changed.emit(position)

    def _on_slider_released(self) -> None:
        """Emit the final position when the user releases the seek slider.

        Only emits if the position differs from the last position already
        emitted during the drag, so a drag that ended on ``sliderMoved`` is not
        reported twice.
        """
        if self._dragging:
            self._dragging = False
            value = self._position_slider.value()
            if value != self._last_seek_position:
                self._last_seek_position = value
                self.position_changed.emit(value)

    def _on_volume_changed(self, value: int) -> None:
        """Emit volume_changed when the volume slider moves."""
        if self._updating:
            return
        self.volume_changed.emit(value / 100.0)
        self._volume_label.setText(f"{value}%")

    # --- Public API ---

    def set_playing(self, playing: bool) -> None:
        """Update button states for playing/paused."""
        self._play_button.setEnabled(not playing)
        self._pause_button.setEnabled(playing)

    def set_duration(self, duration_ms: int) -> None:
        """Set the total duration of the track."""
        self._duration_ms = max(0, duration_ms)
        if not self._dragging:
            self._position_slider.setRange(0, self._duration_ms)
        self._position_slider.setEnabled(self._duration_ms > 0)
        self._duration_label.setText(self._format_time(self._duration_ms))

    def set_position(self, position_ms: int) -> None:
        """Set the current playback position (skipped while dragging)."""
        self._position_ms = position_ms
        if self._dragging:
            return
        self._updating = True
        self._position_slider.setValue(position_ms)
        self._updating = False
        self.set_current_time(position_ms)

    def set_current_time(self, position_ms: int) -> None:
        """Update the current time label."""
        self._position_label.setText(self._format_time(position_ms))

    def set_volume(self, volume: float) -> None:
        """Set the volume slider (0.0-1.0) without emitting a change."""
        self._updating = True
        self._volume_slider.setValue(int(volume * 100))
        self._updating = False
        self._volume_label.setText(f"{int(volume * 100)}%")

    @staticmethod
    def _format_time(ms: int) -> str:
        """Format milliseconds as ``m:ss``."""
        ms = max(0, ms)
        minutes = ms // 60000
        seconds = (ms % 60000) // 1000
        return f"{minutes}:{seconds:02d}"
