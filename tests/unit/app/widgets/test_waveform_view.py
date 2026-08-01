"""Tests for the WaveformView widget."""

from __future__ import annotations

import numpy as np

from app.widgets.waveform_view import WaveformView


def _mono_audio(duration: float = 1.0, sample_rate: int = 44100) -> np.ndarray:
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    return np.sin(2 * np.pi * 440 * t).astype(np.float32)


class TestWaveformView:
    def test_set_audio_data_mono(self, qapp) -> None:
        view = WaveformView()
        view.set_audio_data(_mono_audio(), 44100)
        assert view._audio_data is not None
        x, y = view._plot_data.getData()
        assert len(x) > 0

    def test_set_audio_data_stereo_is_monoized(self, qapp) -> None:
        view = WaveformView()
        left = _mono_audio()
        right = np.roll(left, 10)
        stereo = np.stack([left, right])
        view.set_audio_data(stereo, 44100)
        assert view._audio_data.shape == (2, 44100)

    def test_long_audio_is_downsampled(self, qapp) -> None:
        view = WaveformView()
        view.set_audio_data(_mono_audio(duration=30.0), 44100)
        x, _ = view._plot_data.getData()
        # Decimation keeps ~2000 points (bound of the strided slice)
        assert len(x) <= 2002

    def test_set_position_moves_indicator(self, qapp) -> None:
        view = WaveformView()
        view.set_audio_data(_mono_audio(), 44100)
        view.set_position(0.5)
        assert view._position_line.value() == 0.5

    def test_clear_resets_display(self, qapp) -> None:
        view = WaveformView()
        view.set_audio_data(_mono_audio(), 44100)
        view.clear()
        assert view._audio_data is None
