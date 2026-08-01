"""Waveform view widget for audio visualization."""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QWidget


class WaveformView(QWidget):
    """Widget for displaying audio waveform."""

    def __init__(self) -> None:
        super().__init__()
        self._audio_data: np.ndarray | None = None
        self._position_line = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Create plot widget
        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground("w")  # White background
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.setLabel("left", "Amplitude")
        self._plot_widget.setLabel("bottom", "Time", "s")
        self._plot_widget.setMouseEnabled(x=False, y=False)  # Disable mouse interaction
        layout.addWidget(self._plot_widget)

        # Initialize plot data
        self._plot_data = self._plot_widget.plot(pen="b")

        # Position indicator line
        self._position_line = self._plot_widget.addLine(x=0, pen=pg.mkPen("r", width=2))
        self._position_line.hide()

    def set_audio_data(self, audio_data: np.ndarray, sample_rate: int = 44100) -> None:
        """Set the audio data to display.

        Args:
            audio_data: Audio samples as numpy array (mono or stereo)
            sample_rate: Sample rate in Hz
        """
        self._audio_data = audio_data

        # Convert to mono if stereo for display
        if audio_data.ndim == 2:
            display_data = np.mean(np.abs(audio_data), axis=0)
        else:
            display_data = np.abs(audio_data)

        # Downsample for display if too long
        max_points = 2000
        if len(display_data) > max_points:
            # Simple decimation
            step = len(display_data) // max_points
            display_data = display_data[::step]
            time_step = step / sample_rate
        else:
            time_step = 1.0 / sample_rate

        times = np.arange(len(display_data)) * time_step
        self._plot_data.setData(times, display_data)

        # Set x-axis range
        total_time = (
            len(audio_data) / sample_rate
            if audio_data.ndim == 1
            else len(audio_data[0]) / sample_rate
        )
        self._plot_widget.setXRange(0, total_time)

        # Show position line
        self._position_line.show()

    def set_position(self, position_seconds: float) -> None:
        """Set the playback position indicator.

        Args:
            position_seconds: Current playback position in seconds
        """
        if self._position_line is not None:
            self._position_line.setPos(position_seconds)

    def clear(self) -> None:
        """Clear the waveform display."""
        self._audio_data = None
        self._plot_data.setData([], [])
        self._position_line.hide()
