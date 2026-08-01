"""Separation service orchestrating the full pipeline."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

import numpy as np
from loguru import logger

from engine.audio.loader import AudioLoader
from engine.audio.postprocessor import AudioPostprocessor
from engine.demucs.config import SeparationConfig
from engine.demucs.errors import InvalidAudioError, ProcessingError, SeparationError
from engine.demucs.separator import DemucsSeparator, SeparationState

ProgressCallback = Callable[[int, str], None]


class SeparationService:
    """Orchestrate audio loading, separation, and postprocessing."""

    def __init__(self, config: SeparationConfig) -> None:
        self._config = config
        self._loader = AudioLoader()
        self._postprocessor = AudioPostprocessor()
        self._separator: DemucsSeparator | None = None

    async def initialize(self) -> None:
        """Initialize the separation engine."""
        if self._separator is None:
            self._separator = DemucsSeparator(self._config)
            await self._separator.initialize()

    async def separate(
        self,
        file_path: Path,
        progress_callback: ProgressCallback | None = None,
    ) -> dict[str, np.ndarray]:
        """Run full separation pipeline on an audio file.

        Args:
            file_path: Path to input audio file.
            progress_callback: Optional callback receiving (percent, message).

        Returns:
            Dict of stem_name -> numpy array.
        """
        start = time.monotonic()
        logger.info(f"SeparationService.separate: {file_path}")

        def combined_progress(percent: int) -> None:
            if progress_callback is not None:
                sep = self._separator
                state = sep.state if sep else SeparationState.IDLE
                message = self._state_message(state, percent)
                progress_callback(percent, message)

        if self._separator is None:
            self._separator = DemucsSeparator(
                self._config, progress_callback=combined_progress
            )
            await self._separator.initialize()

        try:
            result = await self._separator.separate_file(file_path)
            elapsed = time.monotonic() - start
            logger.info(f"Separation complete in {elapsed:.2f}s: {list(result.keys())}")
            return result
        except InvalidAudioError:
            raise
        except SeparationError as e:
            logger.error(f"Separation failed: {e}")
            raise ProcessingError(f"Separation pipeline failed: {e}") from e

    def _state_message(self, state: SeparationState, percent: int) -> str:
        messages = {
            SeparationState.IDLE: "Preparing...",
            SeparationState.LOADING: f"Loading model... {percent}%",
            SeparationState.PROCESSING: f"Processing... {percent}%",
            SeparationState.COMPLETE: f"Complete {percent}%",
            SeparationState.ERROR: "Error occurred",
        }
        return messages.get(state, f"Processing... {percent}%")
