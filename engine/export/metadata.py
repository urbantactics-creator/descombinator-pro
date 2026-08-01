"""Metadata embedding for exported audio files."""

from __future__ import annotations

import logging
from pathlib import Path

from mutagen.flac import FLAC
from mutagen.id3 import ID3, TALB, TCON, TIT2, TPE1
from mutagen.mp4 import MP4

from engine.export.errors import MetadataError

logger = logging.getLogger(__name__)


class MetadataEmbedder:
    """Embed metadata into exported audio files."""

    async def embed(
        self,
        path: Path,
        metadata: dict[str, str | None],
    ) -> None:
        """Embed metadata into file based on extension."""
        suffix = path.suffix.lower()
        try:
            if suffix in (".mp3",):
                await self._embed_mp3(path, metadata)
            elif suffix in (".flac",):
                await self._embed_flac(path, metadata)
            elif suffix in (".m4a", ".mp4"):
                await self._embed_m4a(path, metadata)
            elif suffix in (".wav",):
                await self._embed_wav(path, metadata)
            else:
                logger.debug(f"Metadata embedding not supported for {suffix}, skipping")
        except MetadataError:
            raise
        except Exception as e:
            logger.error(f"Failed to embed metadata for {path}: {e}")
            raise MetadataError(f"Cannot embed metadata in {path.name}: {e}") from e

    async def _embed_mp3(self, path: Path, meta: dict[str, str | None]) -> None:
        """Embed ID3 tags for MP3."""
        try:
            audio = ID3(str(path))
        except Exception:
            audio = ID3()

        if meta.get("title"):
            audio.add(TIT2(encoding=3, text=[meta["title"]]))
        if meta.get("artist"):
            audio.add(TPE1(encoding=3, text=[meta["artist"]]))
        if meta.get("album"):
            audio.add(TALB(encoding=3, text=[meta["album"]]))
        if meta.get("genre"):
            audio.add(TCON(encoding=3, text=[meta["genre"]]))

        audio.save(str(path))
        logger.info(f"Embedded ID3 tags for {path.name}")

    async def _embed_flac(self, path: Path, meta: dict[str, str | None]) -> None:
        """Embed Vorbis comments for FLAC."""
        audio = FLAC(str(path))

        if meta.get("title"):
            audio["TITLE"] = [meta["title"]]
        if meta.get("artist"):
            audio["ARTIST"] = [meta["artist"]]
        if meta.get("album"):
            audio["ALBUM"] = [meta["album"]]
        if meta.get("genre"):
            audio["GENRE"] = [meta["genre"]]

        audio.save()
        logger.info(f"Embedded Vorbis comments for {path.name}")

    async def _embed_m4a(self, path: Path, meta: dict[str, str | None]) -> None:
        """Embed MP4 atoms for M4A."""
        audio = MP4(str(path))

        if meta.get("title"):
            audio["\xa9nam"] = [meta["title"]]
        if meta.get("artist"):
            audio["\xa9ART"] = [meta["artist"]]
        if meta.get("album"):
            audio["\xa9alb"] = [meta["album"]]
        if meta.get("genre"):
            audio["\xa9gen"] = [meta["genre"]]

        audio.save()
        logger.info(f"Embedded MP4 atoms for {path.name}")

    async def _embed_wav(self, path: Path, meta: dict[str, str | None]) -> None:
        """Embed metadata for WAV (INFO chunk)."""
        try:
            from mutagen.wave import WAVE

            audio = WAVE(str(path))

            if meta.get("title"):
                audio["TITLE"] = [meta["title"]]
            if meta.get("artist"):
                audio["ARTIST"] = [meta["artist"]]
            if meta.get("album"):
                audio["ALBUM"] = [meta["album"]]
            if meta.get("genre"):
                audio["GENRE"] = [meta["genre"]]

            audio.save()
            logger.info(f"Embedded INFO chunk for {path.name}")
        except Exception as e:
            logger.warning(f"WAV metadata embedding not supported for {path.name}: {e}")
