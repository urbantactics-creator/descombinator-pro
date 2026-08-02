"""Tests for AudioPreprocessor."""

import numpy as np
import pytest

from engine.audio.preprocessor import AudioPreprocessor


@pytest.fixture
def preprocessor() -> AudioPreprocessor:
    return AudioPreprocessor()


class TestRemoveDcOffset:
    async def test_removes_dc(
        self, preprocessor: AudioPreprocessor, dc_offset_audio: np.ndarray
    ) -> None:
        result = await preprocessor.remove_dc_offset(dc_offset_audio)
        assert abs(float(np.mean(result))) < 1e-5

    async def test_no_dc(
        self, preprocessor: AudioPreprocessor, mono_audio_3s: np.ndarray
    ) -> None:
        result = await preprocessor.remove_dc_offset(mono_audio_3s)
        np.testing.assert_array_equal(result, mono_audio_3s)

    async def test_returns_copy(
        self, preprocessor: AudioPreprocessor, mono_audio_3s: np.ndarray
    ) -> None:
        result = await preprocessor.remove_dc_offset(mono_audio_3s)
        assert result is not mono_audio_3s

    async def test_output_float32_when_input_float64(
        self, preprocessor: AudioPreprocessor, dc_offset_audio: np.ndarray
    ) -> None:
        result = await preprocessor.remove_dc_offset(dc_offset_audio.astype(np.float64))
        assert result.dtype == np.float32


class TestNormalizePeak:
    async def test_normalizes(
        self, preprocessor: AudioPreprocessor, mono_audio_3s: np.ndarray
    ) -> None:
        result = await preprocessor.normalize_peak(mono_audio_3s, target_db=-1.0)
        peak = float(np.max(np.abs(result)))
        expected = 10 ** (-1.0 / 20)
        assert abs(peak - expected) < 0.01

    async def test_silent_audio(
        self, preprocessor: AudioPreprocessor, silent_audio: np.ndarray
    ) -> None:
        result = await preprocessor.normalize_peak(silent_audio)
        np.testing.assert_array_equal(result, silent_audio)

    async def test_returns_copy(
        self, preprocessor: AudioPreprocessor, mono_audio_3s: np.ndarray
    ) -> None:
        result = await preprocessor.normalize_peak(mono_audio_3s)
        assert result is not mono_audio_3s

    async def test_output_float32_when_input_float64(
        self, preprocessor: AudioPreprocessor, mono_audio_3s: np.ndarray
    ) -> None:
        result = await preprocessor.normalize_peak(mono_audio_3s.astype(np.float64))
        assert result.dtype == np.float32


class TestClipSilence:
    async def test_trims_silence(
        self, preprocessor: AudioPreprocessor, mono_audio_3s: np.ndarray
    ) -> None:
        padded = np.concatenate([np.zeros(44100), mono_audio_3s, np.zeros(44100)])
        result = await preprocessor.clip_silence(padded, 44100)
        assert len(result) < len(padded)

    async def test_no_silence(
        self, preprocessor: AudioPreprocessor, mono_audio_3s: np.ndarray
    ) -> None:
        result = await preprocessor.clip_silence(mono_audio_3s, 44100)
        assert len(result) == len(mono_audio_3s)


class TestPreprocess:
    async def test_full_pipeline(
        self, preprocessor: AudioPreprocessor, mono_audio_3s: np.ndarray
    ) -> None:
        result = await preprocessor.preprocess(mono_audio_3s, 44100, normalize=True)
        assert result.dtype == np.float32
        peak = float(np.max(np.abs(result)))
        assert peak <= 1.0

    async def test_no_normalize(
        self, preprocessor: AudioPreprocessor, mono_audio_3s: np.ndarray
    ) -> None:
        result = await preprocessor.preprocess(mono_audio_3s, 44100, normalize=False)
        np.testing.assert_array_equal(result, mono_audio_3s)
