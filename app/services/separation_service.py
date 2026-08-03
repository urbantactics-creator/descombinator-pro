"""Separation service orchestrating the full pipeline."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from loguru import logger

from engine.audio.loader import AudioLoader
from engine.audio.postprocessor import AudioPostprocessor
from engine.demucs.config import SeparationConfig
from engine.demucs.errors import InvalidAudioError, ProcessingError, SeparationError
from engine.performance.monitor import ResourceMonitor
from engine.performance.thermal import ThermalMonitor, ThermalState

if TYPE_CHECKING:
    from engine.demucs.separator import DemucsSeparator, SeparationState

ProgressCallback = Callable[[int, str], None]


class ThermalError(SeparationError):
    """Separation paused due to critical thermal conditions."""

    def __init__(self, message: str = "Thermal limit exceeded") -> None:
        super().__init__(message)


class SeparationService:
    """Orchestrate audio loading, separation, and postprocessing."""

    def __init__(
        self,
        config: SeparationConfig,
        monitor: ResourceMonitor | None = None,
        thermal_monitor: ThermalMonitor | None = None,
    ) -> None:
        self._config = config
        self._loader = AudioLoader()
        self._postprocessor = AudioPostprocessor()
        self._monitor = monitor
        self._thermal_monitor = thermal_monitor
        self._separator: DemucsSeparator | None = None

    async def initialize(self) -> None:
        """Initialize the separation engine."""
        await self._ensure_separator()

    async def _ensure_separator(
        self,
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        """Lazily create and initialize the separator if not present.

        Args:
            progress_callback: Optional callback receiving (percent, message).
        """
        if self._separator is not None:
            return
        from engine.demucs.separator import DemucsSeparator

        combined: Callable[[int], None] | None = None
        if progress_callback is not None:

            def combined(percent: int) -> None:
                from engine.demucs.separator import SeparationState

                sep = self._separator
                state = sep.state if sep else SeparationState.IDLE
                progress_callback(percent, self._state_message(state, percent))

        self._separator = DemucsSeparator(self._config, progress_callback=combined)
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
        await self._ensure_separator(progress_callback)
        assert self._separator is not None

        if self._monitor is not None:
            await self._monitor.start()
        try:
            if self._thermal_monitor is not None:
                snap = await self._thermal_monitor.sample()
                if snap.state == ThermalState.CRITICAL:
                    raise ThermalError(
                        f"CPU={snap.cpu_temp_c}°C, GPU={snap.gpu_temp_c}°C"
                    )
            result = await self._separator.separate_file(file_path)
            elapsed = time.monotonic() - start
            logger.info(f"Separation complete in {elapsed:.2f}s: {list(result.keys())}")
            return result
        except InvalidAudioError:
            raise
        except ThermalError:
            raise
        except SeparationError as e:
            logger.error(f"Separation failed: {e}")
            raise ProcessingError(f"Separation pipeline failed: {e}") from e
        finally:
            if self._monitor is not None:
                await self._monitor.stop()
                logger.info(f"Resource summary: {self._monitor.summary()}")

    async def separate_loaded(
        self,
        audio: np.ndarray,
        sample_rate: int = 44_100,
        progress_callback: ProgressCallback | None = None,
    ) -> dict[str, np.ndarray]:
        """Separate audio that is already decoded, avoiding a second decode.

        Reuses the audio loaded by the UI for waveform display, so a large file
        is decoded only once. ``separate_file`` remains for CLI/integrations.

        Args:
            audio: Input audio as float32 numpy array.
            sample_rate: Sample rate of the input audio.
            progress_callback: Optional callback receiving (percent, message).

        Returns:
            Dict of stem_name -> numpy array.
        """
        if audio is None or audio.size == 0:
            raise InvalidAudioError("Input audio is empty or None")

        start = time.monotonic()
        await self._ensure_separator(progress_callback)
        assert self._separator is not None

        if self._monitor is not None:
            await self._monitor.start()
        try:
            if self._thermal_monitor is not None:
                snap = await self._thermal_monitor.sample()
                if snap.state == ThermalState.CRITICAL:
                    raise ThermalError(
                        f"CPU={snap.cpu_temp_c}°C, GPU={snap.gpu_temp_c}°C"
                    )
            result = await self._separator.separate(audio, sample_rate)
            elapsed = time.monotonic() - start
            logger.info(f"Separation complete in {elapsed:.2f}s: {list(result.keys())}")
            return result
        except InvalidAudioError:
            raise
        except ThermalError:
            raise
        except SeparationError as e:
            logger.error(f"Separation failed: {e}")
            raise ProcessingError(f"Separation pipeline failed: {e}") from e
        finally:
            if self._monitor is not None:
                await self._monitor.stop()
                logger.info(f"Resource summary: {self._monitor.summary()}")

    def _state_message(self, state: SeparationState, percent: int) -> str:
        from engine.demucs.separator import SeparationState

        messages = {
            SeparationState.IDLE: "Preparing...",
            SeparationState.LOADING: f"Loading model... {percent}%",
            SeparationState.PROCESSING: f"Processing... {percent}%",
            SeparationState.PAUSED: "Paused — thermal limit",
            SeparationState.COMPLETE: f"Complete {percent}%",
            SeparationState.ERROR: "Error occurred",
        }
        return messages.get(state, f"Processing... {percent}%")
