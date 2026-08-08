"""Tests for MetadataEmbedder."""

import asyncio
from pathlib import Path

import numpy as np
import pytest

from engine.export.metadata import MetadataEmbedder


@pytest.fixture
def metadata_embedder() -> MetadataEmbedder:
    """Return a metadata embedder."""
    return MetadataEmbedder()


@pytest.fixture
def sample_audio() -> np.ndarray:
    """Return sample audio data."""
    return np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100)).astype(np.float32)


class TestMetadataEmbedder:
    async def test_embed_wav(
        self,
        metadata_embedder: MetadataEmbedder,
        sample_audio: np.ndarray,
        tmp_output_dir: Path,
    ) -> None:
        """Test embedding metadata in WAV file."""
        output_path = tmp_output_dir / "test.wav"

        import soundfile as sf

        await asyncio.to_thread(sf.write, str(output_path), sample_audio, 44100)

        metadata = {
            "title": "Test Song",
            "artist": "Test Artist",
            "album": "Test Album",
            "genre": "Test Genre",
        }
        await metadata_embedder.embed(output_path, metadata)

        assert output_path.exists()

    async def test_embed_flac(
        self,
        metadata_embedder: MetadataEmbedder,
        sample_audio: np.ndarray,
        tmp_output_dir: Path,
    ) -> None:
        """Test embedding metadata in FLAC file."""
        output_path = tmp_output_dir / "test.flac"

        import soundfile as sf

        await asyncio.to_thread(sf.write, str(output_path), sample_audio, 44100)

        metadata = {
            "title": "Test Song",
            "artist": "Test Artist",
            "album": "Test Album",
            "genre": "Test Genre",
        }
        await metadata_embedder.embed(output_path, metadata)

        assert output_path.exists()

    async def test_embed_mp3(
        self,
        metadata_embedder: MetadataEmbedder,
        sample_audio: np.ndarray,
        tmp_output_dir: Path,
    ) -> None:
        """Test embedding metadata in MP3 file."""
        output_path = tmp_output_dir / "test.mp3"

        import soundfile as sf

        await asyncio.to_thread(sf.write, str(output_path), sample_audio, 44100)

        metadata = {
            "title": "Test Song",
            "artist": "Test Artist",
            "album": "Test Album",
            "genre": "Test Genre",
        }
        await metadata_embedder.embed(output_path, metadata)

        assert output_path.exists()

    async def test_embed_m4a(
        self,
        metadata_embedder: MetadataEmbedder,
        sample_audio: np.ndarray,
        tmp_output_dir: Path,
    ) -> None:
        """Test embedding metadata in M4A file."""
        output_path = tmp_output_dir / "test.m4a"

        # Create a temporary WAV file first since soundfile doesn't support M4A
        import soundfile as sf

        temp_wav = tmp_output_dir / "temp.wav"
        await asyncio.to_thread(sf.write, str(temp_wav), sample_audio, 44100)

        # Copy the WAV file to M4A using ffmpeg if available
        import subprocess

        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(temp_wav),
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-ar",
                "44100",
                str(output_path),
            ]
            await asyncio.to_thread(subprocess.run, cmd, check=True)
            temp_wav.unlink()
        except subprocess.CalledProcessError, FileNotFoundError:
            pytest.skip("ffmpeg not available for M4A test")

        metadata = {
            "title": "Test Song",
            "artist": "Test Artist",
            "album": "Test Album",
            "genre": "Test Genre",
        }
        await metadata_embedder.embed(output_path, metadata)

        assert output_path.exists()

    async def test_embed_empty_metadata(
        self,
        metadata_embedder: MetadataEmbedder,
        sample_audio: np.ndarray,
        tmp_output_dir: Path,
    ) -> None:
        """Test embedding empty metadata."""
        output_path = tmp_output_dir / "test.wav"

        import soundfile as sf

        await asyncio.to_thread(sf.write, str(output_path), sample_audio, 44100)

        await metadata_embedder.embed(output_path, {})

        assert output_path.exists()

    async def test_embed_partial_metadata(
        self,
        metadata_embedder: MetadataEmbedder,
        sample_audio: np.ndarray,
        tmp_output_dir: Path,
    ) -> None:
        """Test embedding partial metadata."""
        output_path = tmp_output_dir / "test.wav"

        import soundfile as sf

        await asyncio.to_thread(sf.write, str(output_path), sample_audio, 44100)

        metadata = {
            "title": "Test Song",
            "artist": "Test Artist",
        }
        await metadata_embedder.embed(output_path, metadata)

        assert output_path.exists()
