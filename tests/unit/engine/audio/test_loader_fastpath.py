"""Tests for AudioLoader fast paths (WAV mmap, soundfile, fallbacks)."""

import asyncio
import struct
from pathlib import Path
from unittest.mock import AsyncMock, patch

import numpy as np
import pytest

from engine.audio.errors import AudioLoadError
from engine.audio.loader import AudioLoader


@pytest.fixture
def loader() -> AudioLoader:
    return AudioLoader()


def _write_wav(
    path: Path,
    samples: np.ndarray,
    sample_rate: int,
    bits: int = 16,
    channels: int = 1,
) -> None:
    """Write a minimal PCM WAV fixture."""
    dtype: type[np.generic]
    if bits == 16:
        dtype = np.int16
    elif bits == 24 or bits == 32:
        dtype = np.int32
    else:
        raise ValueError(f"unsupported bits: {bits}")

    scale = float(2 ** (bits - 1)) - 1.0
    data = (np.clip(samples, -1.0, 1.0).astype(np.float64) * scale).astype(dtype)

    bytes_per = bits // 8
    if bits == 24:
        # Expand int32 into 3-byte triplets (little-endian).
        raw = np.zeros(len(data) * 3, dtype=np.uint8)
        arr = data.astype(np.uint32)
        for i, v in enumerate(arr):
            raw[i * 3] = v & 0xFF
            raw[i * 3 + 1] = (v >> 8) & 0xFF
            raw[i * 3 + 2] = (v >> 16) & 0xFF
        byte_data = raw.tobytes()
    else:
        byte_data = data.tobytes()

    header = b"RIFF" + struct.pack("<I", 36 + len(byte_data)) + b"WAVE"
    fmt = struct.pack(
        "<HHIIHH",
        1,
        channels,
        sample_rate,
        sample_rate * channels * bytes_per,
        channels * bytes_per,
        bits,
    )
    data_chunk = b"data" + struct.pack("<I", len(byte_data)) + byte_data
    path.write_bytes(header + b"fmt " + struct.pack("<I", 16) + fmt + data_chunk)


def _sine(n: int = 44100 * 2, freq: float = 440.0) -> np.ndarray:
    return np.sin(2 * np.pi * freq * np.linspace(0, 2, n)).astype(np.float32)


class TestWavFastPath:
    """WAV PCM memmap fast path."""

    async def test_matches_librosa_values(
        self, loader: AudioLoader, tmp_path: Path
    ) -> None:
        """Fast path output matches librosa within float tolerance."""
        import librosa

        path = tmp_path / "sine16.wav"
        expected = _sine()
        _write_wav(path, expected, 44100)

        audio = await loader.load(path)
        reference, _ = await asyncio.to_thread(librosa.load, path, sr=44100, mono=True)

        assert audio.dtype == np.float32
        assert audio.ndim == 1
        assert len(audio) == len(expected)
        np.testing.assert_allclose(audio, reference, atol=1e-6)

    async def test_sixteen_bit_mmap_used(
        self, loader: AudioLoader, tmp_path: Path
    ) -> None:
        """16-bit PCM takes the memmap path (no librosa/soundfile)."""
        path = tmp_path / "sine16.wav"
        _write_wav(path, _sine(), 44100)

        with (
            patch.object(loader, "_load_librosa", new=AsyncMock()) as mock_librosa,
            patch.object(loader, "_load_soundfile", new=AsyncMock()) as mock_sf,
        ):
            audio = await loader.load(path)

        assert audio.ndim == 1
        mock_librosa.assert_not_called()
        mock_sf.assert_not_called()

    async def test_24_bit_pcm(self, loader: AudioLoader, tmp_path: Path) -> None:
        """24-bit PCM is decoded and normalized correctly."""
        path = tmp_path / "sine24.wav"
        _write_wav(path, _sine(), 44100, bits=24)

        audio = await loader.load(path)

        assert audio.dtype == np.float32
        np.testing.assert_allclose(audio, _sine(), atol=2e-3)

    async def test_32_bit_int_pcm(self, loader: AudioLoader, tmp_path: Path) -> None:
        """32-bit int PCM is decoded and normalized correctly."""
        path = tmp_path / "sine32.wav"
        _write_wav(path, _sine(), 44100, bits=32)

        audio = await loader.load(path)

        assert audio.dtype == np.float32
        np.testing.assert_allclose(audio, _sine(), atol=2e-3)

    async def test_resample_to_target_sr(
        self, loader: AudioLoader, tmp_path: Path
    ) -> None:
        """Fast path resamples to the requested sample rate."""
        path = tmp_path / "sine16.wav"
        _write_wav(path, _sine(), 44100)

        audio = await loader.load(path, sr=22050)

        assert len(audio) == 22050 * 2
        # kaiser_best resampling may overshoot slightly; allow small headroom.
        assert float(np.max(np.abs(audio))) <= 1.05

    async def test_stereo_memmap_mono_downmix(
        self, loader: AudioLoader, tmp_path: Path
    ) -> None:
        """Stereo WAV fast path returns mono when requested."""
        path = tmp_path / "stereo16.wav"
        left = _sine()
        right = _sine(44100 * 2, freq=880.0)
        _write_wav(path, np.stack([left, right]).T, 44100, channels=2)

        audio = await loader.load(path)

        assert audio.ndim == 1
        assert len(audio) == 44100 * 2

    async def test_stereo_memmap_keeps_channels(
        self, loader: AudioLoader, tmp_path: Path
    ) -> None:
        """Stereo WAV fast path keeps (channels, samples) when mono=False."""
        path = tmp_path / "stereo16.wav"
        left = _sine()
        right = _sine(44100 * 2, freq=880.0)
        _write_wav(path, np.stack([left, right]).T, 44100, channels=2)

        audio = await loader.load(path, mono=False)

        assert audio.ndim == 2
        assert audio.shape[0] == 2
        assert audio.shape[1] == 44100 * 2

    async def test_stereo_resample_keeps_channels(
        self, loader: AudioLoader, tmp_path: Path
    ) -> None:
        """Stereo (C, N) survives resampling; channels are not corrupted (A5)."""
        path = tmp_path / "stereo16.wav"
        left = _sine(44100 * 2, freq=440.0)
        right = _sine(44100 * 2, freq=880.0)
        _write_wav(path, np.stack([left, right]).T, 44100, channels=2)

        audio = await loader.load(path, sr=22050, mono=False)

        assert audio.shape == (2, 44100)  # 2s at 22050 Hz
        assert not np.array_equal(audio[0], audio[1])
        assert float(np.max(np.abs(audio))) <= 1.05


class TestNonPcmAndFallbacks:
    """soundfile path and librosa fallback."""

    async def test_corrupt_wav_falls_back(
        self, loader: AudioLoader, test_corrupt_wav_path: Path
    ) -> None:
        """A corrupt WAV is rejected cleanly with AudioLoadError.

        Regression (C5): this test previously swallowed AudioLoadError in a
        try/except pass, so a fallback that silently returned garbage would
        still pass. The corrupt fixture (truncated RIFF header, no data chunk)
        cannot be decoded by any backend, so the loader must raise
        AudioLoadError and never return audio.
        """
        with pytest.raises(AudioLoadError):
            await loader.load(test_corrupt_wav_path)

    async def test_empty_wav_falls_back(
        self, loader: AudioLoader, test_empty_wav_path: Path
    ) -> None:
        """An empty WAV loads cleanly as an empty float32 array.

        Regression (C5): this test previously swallowed AudioLoadError in a
        try/except pass, so a broken fallback could not fail the test. The
        empty fixture (header-only WAV, zero-length data chunk) makes the
        memmap fast path decline (n_frames == 0) and the load must complete
        cleanly: float32, size 0, never a raw exception.
        """
        audio = await loader.load(test_empty_wav_path)
        assert audio.dtype == np.float32
        assert audio.size == 0

    async def test_mp3_uses_librosa(
        self, loader: AudioLoader, test_metadata_mp3_path: Path
    ) -> None:
        """MP3 goes through the librosa fallback path."""
        audio = await loader.load(test_metadata_mp3_path)
        assert audio.dtype == np.float32
        assert audio.ndim == 1
        assert len(audio) > 0

    async def test_flac_uses_soundfile(
        self, loader: AudioLoader, test_metadata_flac_path: Path
    ) -> None:
        """FLAC goes through the soundfile path."""
        audio = await loader.load(test_metadata_flac_path)
        assert audio.dtype == np.float32
        assert audio.ndim == 1
        assert len(audio) > 0

    async def test_librosa_fallback_on_soundfile_failure(
        self, loader: AudioLoader, tmp_path: Path
    ) -> None:
        """soundfile failure falls back to librosa for supported formats."""
        path = tmp_path / "fake.flac"
        path.write_bytes(b"not a real flac at all" * 10)

        async def fake_librosa(_path: Path, sr: int, mono: bool) -> np.ndarray:
            return np.zeros(44100, dtype=np.float32)

        mock_librosa = AsyncMock(wraps=fake_librosa)
        with patch.object(loader, "_load_librosa", mock_librosa):
            audio = await loader.load(path)
            assert len(audio) == 44100
            mock_librosa.assert_called_once()
