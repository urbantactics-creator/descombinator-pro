"""Audio file loading with format validation."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import ClassVar

import librosa
import numpy as np
from loguru import logger

from engine.audio.errors import AudioFileNotFoundError, AudioFormatError, AudioLoadError


class AudioLoader:
    """Load audio files into numpy arrays."""

    SUPPORTED_FORMATS: ClassVar[frozenset[str]] = frozenset(
        {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".aiff"}
    )

    def validate_exists(self, path: Path) -> None:
        """Raise if file does not exist."""
        if not path.exists():
            raise AudioFileNotFoundError(f"File not found: {path}")

    def validate_format(self, path: Path) -> None:
        """Raise if format is not supported."""
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise AudioFormatError(
                f"Unsupported format '{path.suffix}' for {path.name}. "
                f"Supported: {', '.join(sorted(self.SUPPORTED_FORMATS))}"
            )

    async def load(
        self,
        path: Path,
        sr: int = 44_100,
        mono: bool = True,
    ) -> np.ndarray:
        """Load audio file into float32 array normalized to [-1, 1]."""
        self.validate_exists(path)
        self.validate_format(path)
        try:
            audio, loaded_sr = await asyncio.to_thread(
                librosa.load, path, sr=sr, mono=mono
            )
            duration = len(audio) / loaded_sr
            logger.info(
                f"Loaded {path.name}: shape={audio.shape}, sr={loaded_sr}, "
                f"duration={duration:.2f}s"
            )
            return audio
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
            raise AudioLoadError(f"Cannot load {path.name}: {e}") from e
