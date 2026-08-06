"""Waveform view widget for audio visualization."""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QWidget


def decimate_waveform(
    audio: np.ndarray,
    max_points: int = 2000,
    sample_rate: int = 44_100,
) -> tuple[np.ndarray, float]:
    """Compute peak amplitude per bucket for waveform display.

    The audio is reduced to at most ``max_points`` buckets, each holding the
    peak absolute value of its samples. Processing is done in chunks so large
    files never build a full ``np.abs`` transient in memory.

    Args:
        audio: Input audio as 1D (mono) or 2D (channels, samples) float array.
        max_points: Maximum number of display buckets.
        sample_rate: Sample rate used to compute the time step.

    Returns:
        Tuple of (display_points, time_step) where time_step is seconds per
        bucket.
    """
    mono = np.mean(audio, axis=0).astype(np.float32) if audio.ndim == 2 else audio
    n = len(mono)
    if n == 0:
        return np.array([], dtype=np.float32), 1.0 / sample_rate

    step = max(1, n // max_points)
    n_buckets = n // step
    if n_buckets == 0:
        n_buckets = 1

    display = np.empty(n_buckets, dtype=np.float32)
    block_buckets = max(1, 1_000_000 // step)
    for start in range(0, n_buckets, block_buckets):
        end = min(start + block_buckets, n_buckets)
        lo = start * step
        hi = end * step
        block = np.abs(mono[lo:hi]).reshape(end - start, step)
        display[start:end] = np.max(block, axis=1)
    return display, step / sample_rate


class WaveformView(QWidget):
    """Widget for displaying audio waveform."""

    def __init__(self) -> None:
        """Initialize the waveform view widget."""
        super().__init__()
        self._audio_data: np.ndarray | None = None
        self._position_line = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the plot widget and position indicator."""
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

    def set_display_data(
        self,
        points: np.ndarray,
        time_step: float,
        total_time: float,
    ) -> None:
        """Render pre-decimated display points.

        Args:
            points: Peak amplitudes per bucket.
            time_step: Seconds per bucket.
            total_time: Total audio duration in seconds.
        """
        times = np.arange(len(points)) * time_step
        self._plot_data.setData(times, points)
        self._plot_widget.setXRange(0, total_time)
        self._position_line.show()

    def set_audio_data(self, audio_data: np.ndarray, sample_rate: int = 44100) -> None:
        """Set the audio data to display.

        Args:
            audio_data: Audio samples as numpy array (mono or stereo)
            sample_rate: Sample rate in Hz
        """
        self._audio_data = audio_data

        display_data, time_step = decimate_waveform(audio_data, sample_rate=sample_rate)

        total_time = (
            len(audio_data) / sample_rate
            if audio_data.ndim == 1
            else len(audio_data[0]) / sample_rate
        )
        self.set_display_data(display_data, time_step, total_time)

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
