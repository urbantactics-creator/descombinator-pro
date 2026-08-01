"""Tests for the WaveformView widget."""

from __future__ import annotations

import numpy as np

from app.widgets.waveform_view import WaveformView, decimate_waveform


def _mono_audio(duration: float = 1.0, sample_rate: int = 44100) -> np.ndarray:
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    return np.sin(2 * np.pi * 440 * t).astype(np.float32)


class TestDecimateWaveform:
    def test_mono_short_audio_keeps_points(self) -> None:
        """Audio under max_points is not over-decimated."""
        audio = np.ones(100, dtype=np.float32)
        points, time_step = decimate_waveform(audio, max_points=2000, sample_rate=100)
        assert len(points) == 100
        assert np.allclose(points, 1.0)
        assert time_step == 1.0 / 100

    def test_long_audio_capped_at_max_points(self) -> None:
        """Audio longer than max_points is reduced to <= max_points buckets."""
        audio = np.ones(44100 * 60, dtype=np.float32)
        points, time_step = decimate_waveform(audio, max_points=2000, sample_rate=44100)
        assert len(points) <= 2000
        assert len(points) > 0
        assert np.allclose(points, 1.0)
        assert time_step == (44100 * 60 // 2000) / 44100

    def test_peak_amplitude_per_bucket(self) -> None:
        """Each bucket holds the peak absolute value of its samples."""
        audio = np.zeros(200, dtype=np.float32)
        audio[0] = 0.7
        audio[150] = -0.9
        points, _ = decimate_waveform(audio, max_points=100, sample_rate=100)
        assert points[0] == 0.7
        # sample 150 lands in bucket 75 with step=2 (buckets of 2 samples).
        assert np.isclose(points[75], 0.9)

    def test_stereo_input_monoized(self) -> None:
        """Stereo audio is downmixed before decimation."""
        left = np.ones(4000, dtype=np.float32) * 0.5
        right = np.ones(4000, dtype=np.float32) * 0.5
        stereo = np.stack([left, right])
        points, _ = decimate_waveform(stereo, max_points=2000, sample_rate=100)
        assert len(points) <= 2000
        assert np.allclose(points, 0.5)

    def test_silence_returns_zero_buckets(self) -> None:
        """Silent audio yields all-zero buckets."""
        audio = np.zeros(44100, dtype=np.float32)
        points, _ = decimate_waveform(audio, sample_rate=44100)
        assert len(points) > 0
        assert np.all(points == 0.0)

    def test_time_step_scales_with_sample_rate(self) -> None:
        """time_step is seconds per bucket, so halving the rate doubles it."""
        audio = np.ones(44100, dtype=np.float32)
        _, step_441 = decimate_waveform(audio, max_points=441, sample_rate=44100)
        _, step_220 = decimate_waveform(audio, max_points=441, sample_rate=22050)
        # Same bucketing (step=100 samples) → time per bucket scales with 1/sr.
        assert np.isclose(step_441 * 2, step_220)


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
