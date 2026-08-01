"""Audio metadata reading and writing."""

from __future__ import annotations

import asyncio
from pathlib import Path

import mutagen
import soundfile as sf
from loguru import logger
from pydantic import BaseModel

from engine.audio.errors import MetadataError


class AudioMetadata(BaseModel):
    """Audio file metadata model."""

    title: str | None = None
    artist: str | None = None
    album: str | None = None
    duration: float
    sample_rate: int
    channels: int
    format: str
    bit_depth: str | None = None


class MetadataReader:
    """Read metadata from audio files."""

    async def read(self, path: Path) -> AudioMetadata:
        """Read metadata using soundfile (WAV/FLAC) or mutagen (MP3/M4A/OGG)."""
        try:
            info = await asyncio.to_thread(sf.info, str(path))
            metadata = AudioMetadata(
                duration=info.duration,
                sample_rate=info.samplerate,
                channels=info.channels,
                format=info.format,
                bit_depth=getattr(info, "subtype_info", None),  # type: ignore[arg-type]
            )
            logger.debug(f"Read metadata for {path.name}: {metadata.duration:.2f}s")
            return metadata
        except Exception as e:
            logger.error(f"Failed to read metadata for {path}: {e}")
            raise MetadataError(f"Cannot read metadata: {e}") from e


class MetadataWriter:
    """Write metadata to audio files (WAV/FLAC/MP3/OGG)."""

    async def write(self, path: Path, metadata: AudioMetadata) -> None:
        """Write metadata to file. Supports WAV/FLAC/MP3/OGG."""
        try:
            audio_file = mutagen.File(str(path))
            if audio_file is None:
                raise MetadataError(f"Cannot open {path.name} for writing")

            fmt = path.suffix.lower()
            if fmt in (".wav", ".aiff"):
                from mutagen.id3 import TALB, TIT2, TPE1

                if audio_file.tags is None:
                    audio_file.add_tags()
                tags = audio_file.tags
                if metadata.title:
                    tags.add(TIT2(encoding=3, text=[metadata.title]))
                if metadata.artist:
                    tags.add(TPE1(encoding=3, text=[metadata.artist]))
                if metadata.album:
                    tags.add(TALB(encoding=3, text=[metadata.album]))
            else:
                if metadata.title:
                    audio_file["title"] = metadata.title
                if metadata.artist:
                    audio_file["artist"] = metadata.artist
                if metadata.album:
                    audio_file["album"] = metadata.album

            audio_file.save()
            logger.info(f"Wrote metadata for {path.name}")
        except MetadataError:
            raise
        except Exception as e:
            logger.error(f"Failed to write metadata for {path}: {e}")
            raise MetadataError(f"Cannot write metadata: {e}") from e
