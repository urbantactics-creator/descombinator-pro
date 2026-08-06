"""Tests for MetadataReader and MetadataWriter."""

from pathlib import Path
from unittest.mock import patch

import mutagen
import pytest

from engine.audio.errors import MetadataError
from engine.audio.metadata import AudioMetadata, MetadataReader, MetadataWriter


@pytest.fixture
def reader() -> MetadataReader:
    return MetadataReader()


@pytest.fixture
def test_metadata_mp3_path() -> Path:
    """Path to the MP3 metadata fixture."""
    return Path("tests/fixtures/test_metadata.mp3")


@pytest.fixture
def writer() -> MetadataWriter:
    return MetadataWriter()


class TestMetadataReader:
    async def test_read_wav(
        self, reader: MetadataReader, sample_wav_path: Path
    ) -> None:
        metadata = await reader.read(sample_wav_path)
        assert metadata.sample_rate == 44100
        assert metadata.channels == 1
        assert metadata.format == "WAV"
        assert metadata.duration > 2.5

    async def test_read_stereo(
        self, reader: MetadataReader, sample_stereo_path: Path
    ) -> None:
        metadata = await reader.read(sample_stereo_path)
        assert metadata.channels == 2
        assert metadata.sample_rate == 44100

    async def test_read_missing_file(self, reader: MetadataReader) -> None:
        with pytest.raises(MetadataError):
            await reader.read(Path("nonexistent.wav"))

    @pytest.mark.asyncio
    async def test_read_mp3_via_mutagen(
        self, reader: MetadataReader, test_metadata_mp3_path: Path
    ) -> None:
        """MP3 metadata is read via the mutagen fallback (regression A6)."""
        with patch(
            "engine.audio.metadata.sf.info",
            side_effect=RuntimeError("libsndfile cannot parse MP3"),
        ):
            metadata = await reader.read(test_metadata_mp3_path)
        assert metadata.format == "MP3"
        assert metadata.duration > 0.0
        assert metadata.sample_rate > 0


class TestMetadataWriter:
    async def test_write_metadata(
        self,
        writer: MetadataWriter,
        reader: MetadataReader,
        sample_wav_path: Path,
        tmp_path: Path,
    ) -> None:
        import shutil

        copied = tmp_path / "copy.wav"
        shutil.copy2(sample_wav_path, copied)
        meta = AudioMetadata(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration=3.0,
            sample_rate=44100,
            channels=1,
            format="WAV",
        )
        await writer.write(copied, meta)

        audio_file = mutagen.File(str(copied))
        assert audio_file is not None
        assert audio_file.tags is not None
        assert audio_file.tags["TIT2"].text[0] == "Test Song"
        assert audio_file.tags["TPE1"].text[0] == "Test Artist"
        assert audio_file.tags["TALB"].text[0] == "Test Album"

    async def test_write_to_nonexistent(
        self, writer: MetadataWriter, tmp_path: Path
    ) -> None:
        meta = AudioMetadata(duration=1.0, sample_rate=44100, channels=1, format="WAV")
        with pytest.raises(MetadataError):
            await writer.write(tmp_path / "nonexistent.wav", meta)


class TestAudioMetadata:
    def test_model_fields(self) -> None:
        meta = AudioMetadata(duration=1.0, sample_rate=44100, channels=1, format="WAV")
        assert meta.title is None
        assert meta.artist is None
        assert meta.duration == 1.0

    def test_model_with_optional(self) -> None:
        meta = AudioMetadata(
            title="Song",
            artist="Artist",
            album="Album",
            duration=2.0,
            sample_rate=22050,
            channels=2,
            format="FLAC",
            bit_depth="Signed 24 bit PCM",
        )
        assert meta.title == "Song"
        assert meta.bit_depth == "Signed 24 bit PCM"
