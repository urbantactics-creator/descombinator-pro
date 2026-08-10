"""Demucs separation engine orchestrator."""

import asyncio
from collections.abc import Callable
from contextlib import suppress
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from loguru import logger

from engine.demucs.config import SeparationConfig
from engine.demucs.errors import (
    InvalidAudioError,
    ModelLoadError,
    ProcessingError,
    SeparationError,
)
from engine.inference.config import DeviceType, InferenceConfig, ModelName

if TYPE_CHECKING:
    from engine.audio.postprocessor import AudioPostprocessor
    from engine.audio.preprocessor import AudioPreprocessor
    from engine.inference.pipeline import InferencePipeline


class SeparationState(StrEnum):
    """Separation workflow states."""

    IDLE = "idle"
    LOADING = "loading"
    PROCESSING = "processing"
    PAUSED = "paused"
    COMPLETE = "complete"
    ERROR = "error"


ProgressCallback = Callable[[int], None]


class DemucsSeparator:
    """Orchestrate audio separation with progress and state management."""

    def __init__(
        self,
        config: SeparationConfig,
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        """Initialize the separator with configuration and optional progress reporting.

        Args:
            config: Separation configuration.
            progress_callback: Optional callback receiving progress percentage.
        """
        self._config = config
        self._progress_callback = progress_callback
        self._state = SeparationState.IDLE
        self._preprocessor: AudioPreprocessor | None = None
        self._postprocessor: AudioPostprocessor | None = None
        self._pipeline: InferencePipeline | None = None
        self._error: SeparationError | None = None

    @property
    def state(self) -> SeparationState:
        """Current separation state."""
        return self._state

    @property
    def error(self) -> SeparationError | None:
        """Last error if state is ERROR."""
        return self._error

    def _set_state(self, state: SeparationState) -> None:
        """Update the current separation state and log the transition."""
        self._state = state
        logger.debug(f"Separation state: {state}")

    def _report_progress(self, percent: int) -> None:
        """Report progress to the optional progress callback.

        Args:
            percent: Progress percentage clamped to 0-100.
        """
        if self._progress_callback is not None:
            self._progress_callback(max(0, min(100, percent)))

    def _build_inference_config(self) -> InferenceConfig:
        """Build an InferenceConfig from the current separation configuration.

        Returns:
            InferenceConfig derived from SeparationConfig.
        """
        return InferenceConfig(
            model_name=ModelName(self._config.model_name.value),
            device=self._config.device,
            shifts=self._config.shifts,
            overlap=self._config.overlap,
            segment=self._config.segment,
            jobs=self._config.jobs,
            mixed_precision=self._config.mixed_precision,
            pin_memory=self._config.pin_memory,
            target_stems=self._config.output_stems,
        )

    async def initialize(self) -> None:
        """Load model and prepare pipeline."""
        self._set_state(SeparationState.LOADING)
        self._report_progress(5)
        try:
            from engine.audio.postprocessor import AudioPostprocessor
            from engine.audio.preprocessor import AudioPreprocessor
            from engine.inference.model_manager import ModelManager
            from engine.inference.pipeline import InferencePipeline

            inference_config = self._build_inference_config()
            from engine.performance.optimizer import TorchRuntimeOptimizer

            TorchRuntimeOptimizer.configure(
                inference_config.device, inference_config.jobs
            )
            self._preprocessor = AudioPreprocessor()
            self._postprocessor = AudioPostprocessor()
            model_manager = ModelManager(inference_config)

            heartbeat_task = asyncio.create_task(self._model_load_heartbeat())
            try:
                await model_manager.switch_model(inference_config.model_name)
            finally:
                heartbeat_task.cancel()
                with suppress(Exception):
                    await heartbeat_task

            self._pipeline = InferencePipeline(model_manager)
            self._report_progress(20)
            logger.info(
                f"Separator initialized: model={inference_config.model_name.value}, "
                f"device={inference_config.device.value}"
            )
        except ModelLoadError as e:
            self._set_state(SeparationState.ERROR)
            self._error = e
            raise
        except Exception as e:
            self._set_state(SeparationState.ERROR)
            self._error = ModelLoadError(f"Cannot initialize separator: {e}")
            logger.error(f"Separator initialization failed: {e}")
            raise self._error from e

    async def _model_load_heartbeat(self) -> None:
        """Report periodic progress while a model is being loaded."""
        import asyncio

        percent = 6
        while True:
            await asyncio.sleep(3)
            percent = min(percent + 1, 19)
            self._report_progress(percent)

    async def separate(
        self,
        audio: np.ndarray,
        sample_rate: int = 44_100,
    ) -> dict[str, np.ndarray]:
        """Run full separation pipeline.

        Args:
            audio: Input audio as float32 numpy array.
            sample_rate: Sample rate of input audio.

        Returns:
            Dict of stem_name -> numpy array.
        """
        if self._pipeline is None:
            raise SeparationError("Separator not initialized. Call initialize() first.")

        if self._preprocessor is None or self._postprocessor is None:
            raise SeparationError("Separator not initialized. Call initialize() first.")

        if audio is None or audio.size == 0:
            err = InvalidAudioError("Input audio is empty or None")
            self._set_state(SeparationState.ERROR)
            self._error = err
            raise err

        if audio.ndim not in (1, 2):
            err = InvalidAudioError(f"Audio must be 1D or 2D, got {audio.ndim}D")
            self._set_state(SeparationState.ERROR)
            self._error = err
            raise err

        self._set_state(SeparationState.PROCESSING)
        self._report_progress(25)

        try:
            audio = await self._preprocessor.preprocess(
                audio, sample_rate, normalize=True
            )
            self._report_progress(40)

            stems_dict = await self._pipeline.run(audio, sample_rate)
            self._report_progress(75)

            result: dict[str, np.ndarray] = {}
            for name, stem in stems_dict.items():
                result[name] = await self._postprocessor.postprocess(stem, sample_rate)

            self._report_progress(100)
            self._set_state(SeparationState.COMPLETE)
            logger.info(f"Separation complete: {list(result.keys())}")
            return result

        except SeparationError as e:
            self._set_state(SeparationState.ERROR)
            self._error = e
            raise
        except Exception as e:
            self._set_state(SeparationState.ERROR)
            self._error = ProcessingError(f"Separation failed: {e}")
            logger.error(f"Separation failed: {e}")
            raise self._error from e
        finally:
            if self._config.device == DeviceType.CUDA:
                model_manager = getattr(self._pipeline, "_model_manager", None)
                if model_manager is not None:
                    model_manager.free_memory()

    async def separate_file(
        self,
        file_path: Path,
        sample_rate: int = 44_100,
    ) -> dict[str, np.ndarray]:
        """Load audio from file and separate.

        Args:
            file_path: Path to audio file.
            sample_rate: Target sample rate for loading.

        Returns:
            Dict of stem_name -> numpy array.
        """
        from engine.audio.loader import AudioLoader

        loader = AudioLoader()
        loader.validate_exists(file_path)
        loader.validate_format(file_path)

        self._report_progress(10)
        audio = await loader.load(file_path, sr=sample_rate, mono=True)
        return await self.separate(audio, sample_rate)
