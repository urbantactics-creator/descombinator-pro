"""Tests for AudioLoader."""

from pathlib import Path

import numpy as np
import pytest

from engine.audio.errors import AudioFileNotFoundError, AudioFormatError
from engine.audio.loader import AudioLoader


@pytest.fixture
def loader() -> AudioLoader:
    return AudioLoader()


class TestValidateExists:
    def test_exists(self, loader: AudioLoader, sample_wav_path: Path) -> None:
        loader.validate_exists(sample_wav_path)

    def test_not_exists(self, loader: AudioLoader) -> None:
        with pytest.raises(AudioFileNotFoundError):
            loader.validate_exists(Path("nonexistent.wav"))


class TestValidateFormat:
    def test_wav_accepted(self, loader: AudioLoader) -> None:
        loader.validate_format(Path("test.wav"))

    def test_flac_accepted(self, loader: AudioLoader) -> None:
        loader.validate_format(Path("test.flac"))

    def test_mp3_accepted(self, loader: AudioLoader) -> None:
        loader.validate_format(Path("test.mp3"))

    def test_m4a_accepted(self, loader: AudioLoader) -> None:
        loader.validate_format(Path("test.m4a"))

    def test_ogg_accepted(self, loader: AudioLoader) -> None:
        loader.validate_format(Path("test.ogg"))

    def test_aiff_accepted(self, loader: AudioLoader) -> None:
        loader.validate_format(Path("test.aiff"))

    def test_txt_rejected(self, loader: AudioLoader) -> None:
        with pytest.raises(AudioFormatError, match="Unsupported format"):
            loader.validate_format(Path("test.txt"))

    def test_pdf_rejected(self, loader: AudioLoader) -> None:
        with pytest.raises(AudioFormatError, match="Unsupported format"):
            loader.validate_format(Path("test.pdf"))


class TestLoad:
    async def test_load_wav(self, loader: AudioLoader, sample_wav_path: Path) -> None:
        audio = await loader.load(sample_wav_path)
        assert audio.dtype == np.float32
        assert audio.ndim == 1
        assert len(audio) == 44100 * 3  # 3 seconds

    async def test_load_mono(self, loader: AudioLoader, sample_wav_path: Path) -> None:
        audio = await loader.load(sample_wav_path, mono=True)
        assert audio.ndim == 1

    async def test_load_stereo(
        self, loader: AudioLoader, sample_stereo_path: Path
    ) -> None:
        audio = await loader.load(sample_stereo_path, mono=False)
        assert audio.ndim == 2
        assert audio.shape[0] == 2  # librosa returns (channels, samples)

    async def test_load_custom_sr(
        self, loader: AudioLoader, sample_wav_path: Path
    ) -> None:
        audio = await loader.load(sample_wav_path, sr=22050)
        assert len(audio) == 22050 * 3  # 3 seconds at 22050 Hz

    async def test_load_missing_file(self, loader: AudioLoader) -> None:
        with pytest.raises(AudioFileNotFoundError):
            await loader.load(Path("missing.wav"))

    async def test_load_unsupported_format(
        self, loader: AudioLoader, tmp_path: Path
    ) -> None:
        bad_file = tmp_path / "test.txt"
        bad_file.write_text("not audio")
        with pytest.raises(AudioFormatError):
            await loader.load(bad_file)

    async def test_load_values_in_range(
        self, loader: AudioLoader, sample_wav_path: Path
    ) -> None:
        audio = await loader.load(sample_wav_path)
        assert float(np.max(np.abs(audio))) <= 1.0
        assert float(np.min(audio)) >= -1.0
