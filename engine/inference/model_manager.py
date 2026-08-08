"""Model lifecycle management."""

from typing import TYPE_CHECKING, Protocol

from loguru import logger

from engine.inference.config import DeviceType, InferenceConfig, ModelName
from engine.inference.errors import ModelNotFoundError

if TYPE_CHECKING:
    import torch


class SeparationModel(Protocol):
    """Protocol for separation model agents."""

    async def initialize(self) -> None: ...

    async def separate(self, audio: torch.Tensor) -> dict[str, torch.Tensor]: ...

    @property
    def sources(self) -> list[str]: ...


class ModelManager:
    """Manage model lifecycle: load, cache, switch."""

    def __init__(self, config: InferenceConfig | None = None) -> None:
        """Initialize the model manager.

        Args:
            config: Inference configuration. Uses default InferenceConfig if None.
        """
        self._config = config or InferenceConfig()
        self._models: dict[str, SeparationModel] = {}
        self._current_name: str | None = None

    @property
    def current_model(self) -> SeparationModel | None:
        """Currently active model, or None."""
        if self._current_name and self._current_name in self._models:
            return self._models[self._current_name]
        return None

    @property
    def current_model_name(self) -> str | None:
        """Name of currently active model."""
        return self._current_name

    async def load_model(self, name: str | ModelName) -> SeparationModel:
        """Load a model by name. Returns cached instance if available."""
        model_name = name.value if isinstance(name, ModelName) else name

        if model_name in self._models:
            logger.debug(f"Model {model_name} already loaded, returning cache")
            return self._models[model_name]

        model = self._create_model(model_name)
        await model.initialize()
        self._models[model_name] = model
        logger.info(f"Loaded model: {model_name}")
        return model

    async def switch_model(self, name: str | ModelName) -> SeparationModel:
        """Switch to a different model. Loads if not cached."""
        model = await self.load_model(name)
        model_name = name.value if isinstance(name, ModelName) else name
        self._current_name = model_name
        logger.info(f"Switched to model: {model_name}")
        return model

    def get_model(self, name: str | ModelName) -> SeparationModel | None:
        """Get a cached model by name. Returns None if not loaded."""
        model_name = name.value if isinstance(name, ModelName) else name
        return self._models.get(model_name)

    def list_models(self) -> dict[str, bool]:
        """List all known models and their loaded status."""
        return {mn.value: mn.value in self._models for mn in ModelName}

    def _create_model(self, name: str) -> SeparationModel:
        """Factory: create the appropriate agent for a model name."""
        try:
            model_name = ModelName(name)
        except ValueError:
            raise ModelNotFoundError(f"Unknown model: {name}") from None

        config = InferenceConfig(
            model_name=model_name,
            device=self._config.device,
            shifts=self._config.shifts,
            overlap=self._config.overlap,
            segment=self._config.segment,
            jobs=self._config.jobs,
            target_stems=self._config.target_stems,
        )

        if name in (ModelName.HTDEMUCS_FT.value, ModelName.MDX_EXTRA.value):
            from engine.inference.demucs_agent import DemucsAgent

            return DemucsAgent(config)
        elif name == ModelName.UMXHQ.value:
            from engine.inference.openunmix_agent import OpenUnmixAgent

            return OpenUnmixAgent(config)
        else:
            raise ModelNotFoundError(f"Unknown model: {name}")

    async def unload_model(self, name: str | ModelName) -> None:
        """Unload a model to free memory."""
        model_name = name.value if isinstance(name, ModelName) else name
        if model_name in self._models:
            del self._models[model_name]
            if self._current_name == model_name:
                self._current_name = None
            logger.info(f"Unloaded model: {model_name}")

    async def unload_all(self) -> None:
        """Unload every cached model."""
        for name in list(self._models):
            await self.unload_model(name)
        self.free_memory()
        logger.info("All models unloaded")

    def free_memory(self) -> None:
        """Release cached memory: CUDA cache when applicable, then gc.collect()."""
        if self._config.device == DeviceType.CUDA:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        import gc

        gc.collect()
