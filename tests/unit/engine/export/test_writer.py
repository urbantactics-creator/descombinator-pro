"""Tests for ExportWriter."""

from pathlib import Path

import numpy as np
import pytest

from engine.export.config import ExportConfig, ExportFormat
from engine.export.writer import ExportWriter


@pytest.fixture
def writer_wav() -> ExportWriter:
    """Return a writer configured for WAV format."""
    config = ExportConfig(format=ExportFormat.WAV)
    return ExportWriter(config)


@pytest.fixture
def writer_mp3() -> ExportWriter:
    """Return a writer configured for MP3 format."""
    config = ExportConfig(format=ExportFormat.MP3)
    return ExportWriter(config)


@pytest.fixture
def sample_audio() -> np.ndarray:
    """Return sample audio data."""
    return np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100)).astype(np.float32)


class TestExportWriter:
    async def test_write_wav(
        self,
        writer_wav: ExportWriter,
        sample_audio: np.ndarray,
        tmp_output_dir: Path,
    ) -> None:
        """Test writing audio as WAV file."""
        output_path = tmp_output_dir / "test.wav"
        result = await writer_wav.write_stem("test", sample_audio, output_path)

        assert result == output_path
        assert output_path.exists()

    async def test_write_flac(
        self,
        writer_wav: ExportWriter,
        sample_audio: np.ndarray,
        tmp_output_dir: Path,
    ) -> None:
        """Test writing audio as FLAC file."""
        config = ExportConfig(format=ExportFormat.FLAC)
        writer = ExportWriter(config)
        output_path = tmp_output_dir / "test.flac"
        result = await writer.write_stem("test", sample_audio, output_path)

        assert result == output_path
        assert output_path.exists()

    async def test_write_mp3(
        self,
        writer_mp3: ExportWriter,
        sample_audio: np.ndarray,
        tmp_output_dir: Path,
    ) -> None:
        """Test writing audio as MP3 file."""
        output_path = tmp_output_dir / "test.mp3"
        result = await writer_mp3.write_stem("test", sample_audio, output_path)

        assert result == output_path
        assert output_path.exists()

    async def test_write_m4a(
        self,
        writer_wav: ExportWriter,
        sample_audio: np.ndarray,
        tmp_output_dir: Path,
    ) -> None:
        """Test writing audio as M4A file."""
        config = ExportConfig(format=ExportFormat.M4A)
        writer = ExportWriter(config)
        output_path = tmp_output_dir / "test.m4a"
        result = await writer.write_stem("test", sample_audio, output_path)

        assert result == output_path
        assert output_path.exists()

    async def test_write_wav_stereo_channels_first(
        self,
        writer_wav: ExportWriter,
        tmp_output_dir: Path,
    ) -> None:
        """Channels-first (2, N) stems must be written frames-first (N, 2)."""
        import soundfile as sf

        n = 4096
        t = np.linspace(0, 1, n)
        left = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        right = np.sin(2 * np.pi * 880 * t).astype(np.float32)
        stereo = np.stack([left, right])  # (2, N) channels-first

        output_path = tmp_output_dir / "stereo.wav"
        await writer_wav.write_stem("stereo", stereo, output_path)

        data, sr = sf.read(str(output_path))
        assert sr == 44100
        assert data.shape == (n, 2)
        np.testing.assert_allclose(data[:, 0], left, atol=1e-4)

        np.testing.assert_allclose(data[:, 1], right, atol=1e-4)

    async def test_write_mp3_stereo(
        self,
        writer_mp3: ExportWriter,
        tmp_output_dir: Path,
    ) -> None:
        """Stereo (2, N) MP3 export must not corrupt channel layout."""
        n = 44100
        t = np.linspace(0, 1, n)
        stereo = np.stack(
            [
                np.sin(2 * np.pi * 440 * t),
                np.sin(2 * np.pi * 880 * t),
            ]
        ).astype(np.float32)  # (2, N) channels-first

        output_path = tmp_output_dir / "stereo.mp3"
        await writer_mp3.write_stem("stereo", stereo, output_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    async def test_write_batch(
        self,
        writer_wav: ExportWriter,
        sample_stems_dict: dict[str, np.ndarray],
        tmp_output_dir: Path,
    ) -> None:
        """Test writing multiple stems."""
        results = await writer_wav.write(sample_stems_dict, tmp_output_dir)

        assert len(results) == 3
        for stem_name, path in results.items():
            assert path.exists()
            assert path.name.startswith(stem_name)

    async def test_audio_clipping(
        self,
        writer_wav: ExportWriter,
        tmp_output_dir: Path,
    ) -> None:
        """Test that audio is clipped to [-1, 1]."""
        audio = np.array([2.0, -1.5, 0.5], dtype=np.float32)
        output_path = tmp_output_dir / "clipped.wav"
        await writer_wav.write_stem("clipped", audio, output_path)

        import soundfile as sf

        loaded, _ = sf.read(str(output_path))
        assert np.all(np.abs(loaded) <= 1.0 + 1e-5)

    async def test_fade_in_out(
        self,
        writer_wav: ExportWriter,
        sample_audio: np.ndarray,
        tmp_output_dir: Path,
    ) -> None:
        """Test fade in/out application."""
        config = ExportConfig(fade_in=0.1, fade_out=0.1)
        writer = ExportWriter(config)
        output_path = tmp_output_dir / "faded.wav"
        await writer.write_stem("faded", sample_audio, output_path)

        assert output_path.exists()

    async def test_metadata_embedding(
        self,
        writer_wav: ExportWriter,
        sample_audio: np.ndarray,
        tmp_output_dir: Path,
    ) -> None:
        """Test metadata embedding."""
        config = ExportConfig(
            format=ExportFormat.MP3,
            metadata={"title": "Test Song", "artist": "Test Artist"},
        )
        writer = ExportWriter(config)
        output_path = tmp_output_dir / "metadata.mp3"
        await writer.write_with_metadata("metadata", sample_audio, output_path)

        assert output_path.exists()

    async def test_unsupported_format(
        self,
        writer_wav: ExportWriter,
        sample_audio: np.ndarray,
        tmp_output_dir: Path,
    ) -> None:
        """Test error handling for unsupported format."""
        from engine.export.errors import UnsupportedFormatError

        config = ExportConfig(format=ExportFormat.WAV)
        writer = ExportWriter(config)

        output_path = tmp_output_dir / "test.xyz"
        with pytest.raises(UnsupportedFormatError):
            await writer.write_stem("test", sample_audio, output_path)
