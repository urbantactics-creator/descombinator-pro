"""Open-Unmix separation agent."""

import asyncio
from typing import TYPE_CHECKING, Any

from loguru import logger
from openunmix import predict

from engine.inference.config import DeviceType, InferenceConfig
from engine.inference.errors import DeviceError, InferenceError, ModelLoadError
from engine.performance.optimizer import TorchRuntimeOptimizer

if TYPE_CHECKING:
    import torch


class OpenUnmixAgent:
    """Wrapper around openunmix.predict for audio separation."""

    def __init__(self, config: InferenceConfig) -> None:
        self._config = config
        self._separator: Any | None = None
        self._model: Any | None = None

    async def initialize(self) -> None:
        """Load the Open-Unmix model. Must be called before separate()."""
        import torch

        if self._config.device == DeviceType.CUDA and not torch.cuda.is_available():
            raise DeviceError("CUDA requested but no GPU is available on this machine")
        try:
            self._separator = predict
            self._model = await asyncio.to_thread(
                predict.utils.load_separator,
                model_str_or_path=self._config.model_name.value,
                targets=self._config.target_stems,
                device=self._config.device.value,
            )
            logger.info(
                f"Open-Unmix initialized: model={self._config.model_name.value}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Open-Unmix: {e}")
            raise ModelLoadError(f"Cannot load Open-Unmix: {e}") from e

    async def separate(
        self,
        audio: torch.Tensor,
        sample_rate: int = 44_100,
    ) -> dict[str, torch.Tensor]:
        """Separate audio into stems. Returns dict of stem_name -> tensor."""
        if self._separator is None:
            raise InferenceError("Open-Unmix not initialized. Call initialize() first.")

        import torch

        try:
            if (
                self._config.pin_memory
                and self._config.device == DeviceType.CUDA
                and not audio.is_cuda
            ):
                audio = audio.pin_memory()
            # Open-Unmix models are stereo-only: upmix mono input
            # (1, N) to stereo (2, N) before inference. (Regression A7.)
            if audio.ndim == 1:
                audio = audio.unsqueeze(0)
            if audio.shape[0] == 1:
                audio = audio.repeat(2, 1)
            with (
                torch.inference_mode(),
                TorchRuntimeOptimizer.autocast_ctx(
                    self._config.mixed_precision
                    and self._config.device == DeviceType.CUDA,
                    "cuda",
                ),
            ):
                kwargs: dict[str, Any] = {
                    "rate": sample_rate,
                    "targets": self._config.target_stems,
                    "device": self._config.device.value,
                }
                if self._model is not None:
                    kwargs["separator"] = self._model
                else:
                    kwargs["model_str_or_path"] = self._config.model_name.value
                stems_dict = await asyncio.to_thread(
                    self._separator.separate, audio, **kwargs
                )
            result = {name: tensor.squeeze(0) for name, tensor in stems_dict.items()}
            logger.info(f"Open-Unmix separation complete: {list(result.keys())}")
            return result
        except InferenceError:
            raise
        except Exception as e:
            logger.error(f"Open-Unmix separation failed: {e}")
            raise InferenceError(f"Separation failed: {e}") from e

    @property
    def sources(self) -> list[str]:
        """Available stem names."""
        return ["vocals", "drums", "bass", "other"]
