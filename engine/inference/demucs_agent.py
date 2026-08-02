"""Demucs v4 separation agent."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from loguru import logger

from engine.inference.config import DeviceType, InferenceConfig
from engine.inference.errors import DeviceError, InferenceError, ModelLoadError
from engine.performance.optimizer import TorchRuntimeOptimizer

if TYPE_CHECKING:
    import torch


class DemucsAgent:
    """Wrapper around demucs.api.Separator for audio separation."""

    def __init__(self, config: InferenceConfig) -> None:
        self._config = config
        self._separator: Any | None = None

    async def initialize(self) -> None:
        """Load the Demucs model. Must be called before separate()."""
        import torch

        if self._config.device == DeviceType.CUDA and not torch.cuda.is_available():
            raise DeviceError("CUDA requested but no GPU is available on this machine")
        try:
            from demucs.api import Separator

            self._separator = await asyncio.to_thread(
                Separator,
                model=self._config.model_name.value,
                device=self._config.device.value,
                shifts=self._config.shifts,
                overlap=self._config.overlap,
                segment=self._config.segment,
                jobs=self._config.jobs,
            )
            logger.info(
                f"Demucs initialized: model={self._config.model_name.value}, "
                f"device={self._config.device.value}"
            )
        except ModelLoadError:
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Demucs: {e}")
            raise ModelLoadError(f"Cannot load Demucs: {e}") from e

    async def separate(
        self,
        audio: torch.Tensor,
    ) -> dict[str, torch.Tensor]:
        """Separate audio into stems. Returns dict of stem_name -> tensor."""
        if self._separator is None:
            raise InferenceError("Demucs not initialized. Call initialize() first.")

        import torch

        try:
            if (
                self._config.pin_memory
                and self._config.device == DeviceType.CUDA
                and not audio.is_cuda
            ):
                audio = audio.pin_memory()
            with (
                torch.inference_mode(),
                TorchRuntimeOptimizer.autocast_ctx(
                    self._config.mixed_precision
                    and self._config.device == DeviceType.CUDA,
                    "cuda",
                ),
            ):
                result = await asyncio.to_thread(self._separator.separate_tensor, audio)
            _, stems_dict = result
            filtered = {
                name: tensor
                for name, tensor in stems_dict.items()
                if name in self._config.target_stems
            }
            logger.info(f"Demucs separation complete: {list(filtered.keys())}")
            return filtered
        except InferenceError:
            raise
        except Exception as e:
            logger.error(f"Demucs separation failed: {e}")
            raise InferenceError(f"Separation failed: {e}") from e

    @property
    def sources(self) -> list[str]:
        """Available stem names."""
        if self._separator is None:
            return []
        return list(self._separator.model.sources)
