"""Inference pipeline orchestrating model selection and separation."""

import time

import numpy as np
from loguru import logger

from engine.audio.preprocessor import AudioPreprocessor
from engine.inference.errors import InferenceError
from engine.inference.model_manager import ModelManager


class InferencePipeline:
    """Orchestrate: preprocess -> model inference -> postprocess."""

    def __init__(self, model_manager: ModelManager) -> None:
        self._model_manager = model_manager
        self._preprocessor = AudioPreprocessor()

    async def run(
        self,
        audio: np.ndarray,
        sample_rate: int,
        model_name: str | None = None,
    ) -> dict[str, np.ndarray]:
        """Run full separation pipeline.

        Args:
            audio: Input audio as numpy float32 array.
            sample_rate: Sample rate of input audio.
            model_name: Override model (uses config default if None).

        Returns:
            Dict of stem_name -> numpy array.
        """
        start = time.monotonic()

        if model_name:
            model = await self._model_manager.switch_model(model_name)
        else:
            model = self._model_manager.current_model
            if model is None:
                raise InferenceError("No model loaded. Call switch_model() first.")

        audio = await self._preprocessor.preprocess(audio, sample_rate, normalize=True)

        if audio.ndim == 1:
            audio = audio[np.newaxis, :]
        import torch

        tensor = torch.from_numpy(audio).float()

        stems_dict = await model.separate(tensor)

        result = {name: t.cpu().numpy() for name, t in stems_dict.items()}

        elapsed = time.monotonic() - start
        logger.info(
            f"Pipeline complete: {list(result.keys())}, duration={elapsed:.2f}s"
        )
        return result
