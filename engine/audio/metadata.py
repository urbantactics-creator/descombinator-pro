"""Audio metadata reading and writing."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import mutagen
import soundfile as sf
from loguru import logger
from pydantic import BaseModel

from engine.audio.errors import MetadataError


def _tag_text(tags: Any | None, *keys: str) -> str | None:
    """Extract a text tag by trying multiple keys (ID3 / M4A / Vorbis)."""
    if tags is None:
        return None
    for key in keys:
        try:
            value = tags[key]
        except (KeyError, TypeError):
            continue
        if value is None:
            continue
        if hasattr(value, "text") and value.text:
            return str(value.text[0])
        if isinstance(value, (list, tuple)) and value:
            return str(value[0])
        if value:
            return str(value)
    return None


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
        """Read metadata using soundfile (WAV/FLAC) or mutagen (MP3/M4A/OGG).

        soundfile (libsndfile) cannot parse MP3/M4A/OGG, so those formats fall
        back to mutagen. (Regression A6.)
        """
        try:
            return await self._read_soundfile(path)
        except Exception:
            return await self._read_mutagen(path)

    async def _read_soundfile(self, path: Path) -> AudioMetadata:
        """Read metadata via soundfile for libsndfile-supported formats."""
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

    async def _read_mutagen(self, path: Path) -> AudioMetadata:
        """Read metadata via mutagen for formats soundfile cannot parse."""

        def _read() -> AudioMetadata:
            try:
                audio_file = mutagen.File(str(path))
                if audio_file is None:
                    raise MetadataError(f"Cannot read metadata for {path.name}")
                info = getattr(audio_file, "info", None)
                tags = getattr(audio_file, "tags", None)
                return AudioMetadata(
                    title=_tag_text(tags, "TIT2", "\xa9nam", "title"),
                    artist=_tag_text(tags, "TPE1", "\xa9ART", "artist"),
                    album=_tag_text(tags, "TALB", "\xa9alb", "album"),
                    duration=float(getattr(info, "length", 0.0) or 0.0),
                    sample_rate=int(getattr(info, "sample_rate", 0) or 0),
                    channels=int(getattr(info, "channels", 0) or 0),
                    format=path.suffix.lstrip(".").upper() or "UNKNOWN",
                    bit_depth=None,
                )
            except MetadataError:
                raise
            except Exception as e:
                raise MetadataError(f"Cannot read metadata for {path.name}") from e

        return await asyncio.to_thread(_read)


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
