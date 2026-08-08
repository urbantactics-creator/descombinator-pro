"""Unit tests for ModelManager."""

from unittest.mock import AsyncMock, patch

import pytest

from engine.inference.config import ModelName
from engine.inference.errors import ModelNotFoundError
from engine.inference.model_manager import ModelManager


@pytest.fixture
def manager() -> ModelManager:
    return ModelManager()


class TestModelManagerLoad:
    @pytest.mark.asyncio
    async def test_load_demucs(self, manager: ModelManager) -> None:
        with patch.object(manager, "_create_model") as mock_create:
            mock_model = AsyncMock()
            mock_create.return_value = mock_model
            result = await manager.load_model(ModelName.HTDEMUCS_FT)
            assert result is mock_model
            mock_model.initialize.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_load_returns_cached(self, manager: ModelManager) -> None:
        with patch.object(manager, "_create_model") as mock_create:
            mock_model = AsyncMock()
            mock_create.return_value = mock_model
            first = await manager.load_model(ModelName.HTDEMUCS_FT)
            second = await manager.load_model(ModelName.HTDEMUCS_FT)
            assert first is second
            mock_create.assert_called_once()


class TestModelManagerSwitch:
    @pytest.mark.asyncio
    async def test_switch_updates_current(self, manager: ModelManager) -> None:
        with patch.object(manager, "_create_model") as mock_create:
            mock_model = AsyncMock()
            mock_create.return_value = mock_model
            await manager.switch_model(ModelName.UMXHQ)
            assert manager.current_model_name == "umxhq"
            assert manager.current_model is mock_model


class TestModelManagerGet:
    def test_get_returns_none_when_not_loaded(self, manager: ModelManager) -> None:
        assert manager.get_model("nonexistent") is None


class TestModelManagerList:
    @pytest.mark.asyncio
    async def test_list_shows_loaded_status(self, manager: ModelManager) -> None:
        with patch.object(manager, "_create_model") as mock_create:
            mock_model = AsyncMock()
            mock_create.return_value = mock_model
            await manager.load_model(ModelName.HTDEMUCS_FT)
            models = manager.list_models()
            assert models["htdemucs_ft"] is True
            assert models["umxhq"] is False


class TestModelManagerUnload:
    @pytest.mark.asyncio
    async def test_unload_removes_model(self, manager: ModelManager) -> None:
        with patch.object(manager, "_create_model") as mock_create:
            mock_model = AsyncMock()
            mock_create.return_value = mock_model
            await manager.load_model(ModelName.HTDEMUCS_FT)
            await manager.unload_model(ModelName.HTDEMUCS_FT)
            assert manager.get_model(ModelName.HTDEMUCS_FT) is None

    @pytest.mark.asyncio
    async def test_unload_clears_current(self, manager: ModelManager) -> None:
        with patch.object(manager, "_create_model") as mock_create:
            mock_model = AsyncMock()
            mock_create.return_value = mock_model
            await manager.switch_model(ModelName.HTDEMUCS_FT)
            await manager.unload_model(ModelName.HTDEMUCS_FT)
            assert manager.current_model is None
            assert manager.current_model_name is None

    @pytest.mark.asyncio
    async def test_unload_nonexistent_noop(self, manager: ModelManager) -> None:
        await manager.unload_model("nonexistent")


class TestModelManagerCreate:
    def test_create_demucs_agent(self, manager: ModelManager) -> None:
        model = manager._create_model(ModelName.HTDEMUCS_FT.value)
        assert type(model).__name__ == "DemucsAgent"

    def test_create_openunmix_agent(self, manager: ModelManager) -> None:
        model = manager._create_model(ModelName.UMXHQ.value)
        assert type(model).__name__ == "OpenUnmixAgent"

    def test_create_unknown_raises(self, manager: ModelManager) -> None:
        with pytest.raises(ModelNotFoundError, match="Unknown model"):
            manager._create_model("bogus_model")
