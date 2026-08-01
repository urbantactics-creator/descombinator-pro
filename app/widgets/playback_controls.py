"""Playback controls widget."""

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
    """Widget for audio playback controls."""

    play_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()
    position_changed = Signal(int)  # Position in milliseconds
    volume_changed = Signal(float)  # Volume as 0.0-1.0

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        self._duration_ms = 0
        self._position_ms = 0

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

        # Position slider
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("0:00"))

        self._position_slider = QSlider(Qt.Horizontal)
        self._position_slider.setRange(0, 1000)
        self._position_slider.sliderMoved.connect(self._on_position_slider_moved)
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

    def _on_play_clicked(self) -> None:
        self.play_clicked.emit()

    def _on_pause_clicked(self) -> None:
        self.pause_clicked.emit()

    def _on_stop_clicked(self) -> None:
        self.stop_clicked.emit()

    def _on_position_slider_moved(self, position: int) -> None:
        self.position_changed.emit(position)

    def _on_volume_changed(self, value: int) -> None:
        volume = value / 100.0
        self.volume_changed.emit(volume)
        self._volume_label.setText(f"{value}%")

    def set_playing(self, playing: bool) -> None:
        """Update button states for playing/paused."""
        self._play_button.setEnabled(not playing)
        self._pause_button.setEnabled(playing)

    def set_duration(self, duration_ms: int) -> None:
        """Set the total duration of the track."""
        self._duration_ms = duration_ms
        self._position_slider.setRange(0, duration_ms)
        minutes = duration_ms // 60000
        seconds = (duration_ms % 60000) // 1000
        self._duration_label.setText(f"{minutes}:{seconds:02d}")

    def set_position(self, position_ms: int) -> None:
        """Set the current playback position."""
        self._position_ms = position_ms
        self._position_slider.setValue(position_ms)
        minutes = position_ms // 60000
        seconds = (position_ms % 60000) // 1000
        # Update the left time label (we could add a second label for remaining time)
        # For now, just update position display in the slider tooltip or similar
        self._position_slider.setToolTip(f"{minutes}:{seconds:02d}")

    def set_volume(self, volume: float) -> None:
        """Set the volume (0.0-1.0)."""
        self._volume_slider.setValue(int(volume * 100))
        self._volume_label.setText(f"{int(volume * 100)}%")
