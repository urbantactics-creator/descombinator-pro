"""Tests for AudioPostprocessor."""

import numpy as np
import pytest

from engine.audio.postprocessor import AudioPostprocessor


@pytest.fixture
def postprocessor() -> AudioPostprocessor:
    return AudioPostprocessor()


class TestPeakLimit:
    async def test_limits_peaks(self, postprocessor: AudioPostprocessor) -> None:
        audio = np.array([0.5, -0.5, 1.5, -1.0], dtype=np.float32)
        result = await postprocessor.peak_limit(audio, ceiling_db=-0.3)
        ceiling = 10 ** (-0.3 / 20)
        assert float(np.max(np.abs(result))) <= ceiling + 1e-6

    async def test_no_clipping_needed(
        self, postprocessor: AudioPostprocessor, mono_audio_3s: np.ndarray
    ) -> None:
        audio = mono_audio_3s * 0.5
        result = await postprocessor.peak_limit(audio)
        np.testing.assert_array_equal(result, audio)


class TestFadeInOut:
    async def test_fade_edges(
        self, postprocessor: AudioPostprocessor, mono_audio_3s: np.ndarray
    ) -> None:
        result = await postprocessor.fade_in_out(
            mono_audio_3s, 44100, fade_duration=0.01
        )
        assert result[0] == 0.0
        assert result[-1] == 0.0
        assert len(result) == len(mono_audio_3s)

    async def test_short_audio_no_crash(
        self, postprocessor: AudioPostprocessor
    ) -> None:
        audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        result = await postprocessor.fade_in_out(audio, 44100, fade_duration=0.02)
        np.testing.assert_array_equal(result, audio)

    async def test_zero_fade(
        self, postprocessor: AudioPostprocessor, mono_audio_3s: np.ndarray
    ) -> None:
        result = await postprocessor.fade_in_out(
            mono_audio_3s, 44100, fade_duration=0.0
        )
        np.testing.assert_array_equal(result, mono_audio_3s)


class TestCrossfade:
    async def test_equal_length(self, postprocessor: AudioPostprocessor) -> None:
        a = np.ones(1000, dtype=np.float32)
        b = np.zeros(1000, dtype=np.float32)
        result = await postprocessor.crossfade(a, b, 44100, overlap=0.001)
        assert len(result) < len(a) + len(b)
        assert result.dtype == np.float32

    async def test_different_length(self, postprocessor: AudioPostprocessor) -> None:
        a = np.ones(500, dtype=np.float32)
        b = np.zeros(2000, dtype=np.float32)
        result = await postprocessor.crossfade(a, b, 44100, overlap=0.001)
        assert len(result) == 500 + 2000 - int(44100 * 0.001)

    async def test_zero_overlap(self, postprocessor: AudioPostprocessor) -> None:
        a = np.ones(100, dtype=np.float32)
        b = np.zeros(100, dtype=np.float32)
        result = await postprocessor.crossfade(a, b, 44100, overlap=0.0)
        np.testing.assert_array_equal(result, np.concatenate([a, b]))

    async def test_large_overlap_clamped(
        self, postprocessor: AudioPostprocessor
    ) -> None:
        a = np.ones(10, dtype=np.float32)
        b = np.zeros(10, dtype=np.float32)
        result = await postprocessor.crossfade(a, b, 44100, overlap=1.0)
        assert len(result) == 10 + 10 - 10


class TestPostprocess:
    async def test_full_pipeline(
        self, postprocessor: AudioPostprocessor, mono_audio_3s: np.ndarray
    ) -> None:
        result = await postprocessor.postprocess(mono_audio_3s, 44100)
        assert result.dtype == np.float32
        assert result[0] == 0.0
        assert result[-1] == 0.0

    async def test_no_fade(self, postprocessor: AudioPostprocessor) -> None:
        audio = np.array([0.1, -0.1, 0.1], dtype=np.float32)
        result = await postprocessor.postprocess(audio, 44100, fade=False, limit=True)
        assert result[0] != 0.0

    async def test_no_limit(self, postprocessor: AudioPostprocessor) -> None:
        audio = np.array([1.5, -1.5, 0.5], dtype=np.float32)
        result = await postprocessor.postprocess(audio, 44100, fade=False, limit=False)
        np.testing.assert_array_equal(result, audio)
