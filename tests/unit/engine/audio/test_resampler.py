"""Tests for AudioResampler."""

import numpy as np
import pytest

from engine.audio.resampler import AudioResampler


@pytest.fixture
def resampler() -> AudioResampler:
    return AudioResampler()


class TestResample:
    async def test_resample_downsample(
        self, resampler: AudioResampler, mono_audio_3s: np.ndarray
    ) -> None:
        result = await resampler.resample(mono_audio_3s, 44100, 22050)
        expected_len = len(mono_audio_3s) // 2
        assert abs(len(result) - expected_len) < 10
        assert result.dtype == np.float32

    async def test_resample_same_sr(
        self, resampler: AudioResampler, mono_audio_3s: np.ndarray
    ) -> None:
        result = await resampler.resample(mono_audio_3s, 44100, 44100)
        np.testing.assert_array_equal(result, mono_audio_3s)
        assert result is not mono_audio_3s  # should be a copy

    async def test_resample_upsample(
        self, resampler: AudioResampler, mono_audio_3s: np.ndarray
    ) -> None:
        short = mono_audio_3s[:22050]  # 1 second at 44100
        result = await resampler.resample(short, 44100, 48000)
        expected_len = int(len(short) * 48000 / 44100)
        assert abs(len(result) - expected_len) < 10


class TestToMono:
    async def test_stereo_to_mono(
        self, resampler: AudioResampler, stereo_audio_2s: np.ndarray
    ) -> None:
        result = await resampler.to_mono(stereo_audio_2s)
        assert result.ndim == 1
        assert len(result) == stereo_audio_2s.shape[1]

    async def test_mono_unchanged(
        self, resampler: AudioResampler, mono_audio_3s: np.ndarray
    ) -> None:
        result = await resampler.to_mono(mono_audio_3s)
        np.testing.assert_array_equal(result, mono_audio_3s)
        assert result is not mono_audio_3s  # should be a copy


class TestEnsureMono:
    async def test_stereo_resample_combined(
        self, resampler: AudioResampler, stereo_audio_2s: np.ndarray
    ) -> None:
        result = await resampler.ensure_mono(stereo_audio_2s, 44100, 22050)
        assert result.ndim == 1
        expected_len = stereo_audio_2s.shape[1] // 2
        assert abs(len(result) - expected_len) < 10

    async def test_mono_no_resample(
        self, resampler: AudioResampler, mono_audio_3s: np.ndarray
    ) -> None:
        result = await resampler.ensure_mono(mono_audio_3s, 44100, 44100)
        np.testing.assert_array_equal(result, mono_audio_3s)
