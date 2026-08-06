"""Unit tests for InferencePipeline."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest
import torch

from engine.inference.errors import InferenceError
from engine.inference.model_manager import ModelManager
from engine.inference.pipeline import InferencePipeline


@pytest.fixture
def mock_model_manager() -> MagicMock:
    manager = MagicMock(spec=ModelManager)
    return manager


@pytest.fixture
def pipeline(mock_model_manager: MagicMock) -> InferencePipeline:
    return InferencePipeline(mock_model_manager)


class TestInferencePipelineRun:
    @pytest.mark.asyncio
    async def test_run_no_model_raises(
        self, pipeline: InferencePipeline, dummy_audio_numpy: np.ndarray
    ) -> None:
        pipeline._model_manager.current_model = None
        with pytest.raises(InferenceError, match="No model loaded"):
            await pipeline.run(dummy_audio_numpy, 44100)

    @pytest.mark.asyncio
    async def test_run_converts_numpy_to_torch_and_back(
        self,
        pipeline: InferencePipeline,
        dummy_audio_numpy: np.ndarray,
    ) -> None:
        vocals = torch.randn(1, 44100)
        other = torch.randn(1, 44100)
        stems_dict = {"vocals": vocals, "other": other}

        mock_model = AsyncMock()
        mock_model.separate.return_value = stems_dict
        pipeline._model_manager.current_model = mock_model

        result = await pipeline.run(dummy_audio_numpy, 44100)

        assert "vocals" in result
        assert "other" in result
        assert isinstance(result["vocals"], np.ndarray)

    @pytest.mark.asyncio
    async def test_run_with_model_override_switches(
        self,
        pipeline: InferencePipeline,
        dummy_audio_numpy: np.ndarray,
    ) -> None:
        mock_model = AsyncMock()
        mock_model.separate.return_value = {"vocals": torch.randn(1, 44100)}
        pipeline._model_manager.switch_model = AsyncMock(return_value=mock_model)

        result = await pipeline.run(dummy_audio_numpy, 44100, model_name="umxhq")

        pipeline._model_manager.switch_model.assert_awaited_once_with("umxhq")
        assert "vocals" in result

    @pytest.mark.asyncio
    async def test_run_mono_input_expands_channels(
        self,
        pipeline: InferencePipeline,
    ) -> None:
        mono = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100)).astype(np.float32)
        vocals = torch.randn(1, 44100)
        stems_dict = {"vocals": vocals}

        mock_model = AsyncMock()
        mock_model.separate.return_value = stems_dict
        pipeline._model_manager.current_model = mock_model

        result = await pipeline.run(mono, 44100)
        assert "vocals" in result

    @pytest.mark.asyncio
    async def test_run_stereo_input_preserves(
        self,
        pipeline: InferencePipeline,
    ) -> None:
        stereo = np.random.randn(2, 44100).astype(np.float32)
        vocals = torch.randn(2, 44100)
        stems_dict = {"vocals": vocals}

        mock_model = AsyncMock()
        mock_model.separate.return_value = stems_dict
        pipeline._model_manager.current_model = mock_model

        result = await pipeline.run(stereo, 44100)
        assert "vocals" in result
        assert result["vocals"].shape == (2, 44100)
