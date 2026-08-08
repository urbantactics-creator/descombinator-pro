"""Unit tests for OpenUnmixAgent."""

from unittest.mock import MagicMock, patch

import pytest
import torch

from engine.inference.config import InferenceConfig, ModelName
from engine.inference.errors import InferenceError, ModelLoadError
from engine.inference.openunmix_agent import OpenUnmixAgent


@pytest.fixture
def config() -> InferenceConfig:
    return InferenceConfig(model_name=ModelName.UMXHQ)


@pytest.fixture
def agent(config: InferenceConfig) -> OpenUnmixAgent:
    return OpenUnmixAgent(config)


class TestOpenUnmixAgentInit:
    def test_creates_without_error(self, agent: OpenUnmixAgent) -> None:
        assert agent._separator is None
        assert agent.sources == ["vocals", "drums", "bass", "other"]


class TestOpenUnmixAgentInitialize:
    @pytest.mark.asyncio
    async def test_initialize_success(self, agent: OpenUnmixAgent) -> None:
        with patch(
            "engine.inference.openunmix_agent.predict.utils.load_separator",
            return_value=MagicMock(),
        ):
            await agent.initialize()
            assert agent._separator is not None
            assert agent._model is not None

    @pytest.mark.asyncio
    async def test_initialize_import_error(self, agent: OpenUnmixAgent) -> None:
        with (
            patch(
                "engine.inference.openunmix_agent.predict.utils.load_separator",
                side_effect=ImportError("no openunmix"),
            ),
            pytest.raises(ModelLoadError, match="Cannot load Open-Unmix"),
        ):
            await agent.initialize()


class TestOpenUnmixAgentSeparate:
    @pytest.mark.asyncio
    async def test_separate_before_init(
        self, agent: OpenUnmixAgent, dummy_audio_torch: torch.Tensor
    ) -> None:
        with pytest.raises(InferenceError, match="not initialized"):
            await agent.separate(dummy_audio_torch)

    @pytest.mark.asyncio
    async def test_separate_squeezes_batch_dim(
        self, agent: OpenUnmixAgent, dummy_audio_torch: torch.Tensor
    ) -> None:
        vocals_3d = torch.randn(1, 2, 44100)
        other_3d = torch.randn(1, 2, 44100)
        stems_dict = {"vocals": vocals_3d, "other": other_3d}

        mock_predict = MagicMock()
        mock_predict.separate.return_value = stems_dict
        agent._separator = mock_predict

        result = await agent.separate(dummy_audio_torch)

        assert result["vocals"].shape == (2, 44100)
        assert result["other"].shape == (2, 44100)

    @pytest.mark.asyncio
    async def test_separate_generic_error(
        self, agent: OpenUnmixAgent, dummy_audio_torch: torch.Tensor
    ) -> None:
        mock_predict = MagicMock()
        mock_predict.separate.side_effect = RuntimeError("boom")
        agent._separator = mock_predict

        with pytest.raises(InferenceError, match="Separation failed"):
            await agent.separate(dummy_audio_torch)

    @pytest.mark.asyncio
    async def test_separate_upmixes_mono_input(
        self, agent: OpenUnmixAgent, dummy_audio_torch: torch.Tensor
    ) -> None:
        """Mono (1, N) input is upmixed to stereo (2, N) before inference (A7)."""
        mock_predict = MagicMock()
        mock_predict.separate.return_value = {
            "vocals": torch.randn(1, 2, 44100),
            "other": torch.randn(1, 2, 44100),
        }
        agent._separator = mock_predict
        agent._model = MagicMock()

        mono = torch.randn(1, 44100)
        await agent.separate(mono)

        call_audio = mock_predict.separate.call_args.args[0]
        assert call_audio.shape[0] == 2
        assert call_audio.shape[1] == 44100
        assert mock_predict.separate.call_args.kwargs.get("separator") is agent._model
        assert "model_str_or_path" not in mock_predict.separate.call_args.kwargs

    @pytest.mark.asyncio
    async def test_separate_reuses_cached_model(
        self, agent: OpenUnmixAgent, dummy_audio_torch: torch.Tensor
    ) -> None:
        """The model loaded in initialize() is reused across separate() calls (A7)."""
        mock_predict = MagicMock()
        mock_predict.separate.return_value = {
            "vocals": torch.randn(1, 2, 44100),
            "other": torch.randn(1, 2, 44100),
        }
        agent._separator = mock_predict
        agent._model = MagicMock()

        await agent.separate(dummy_audio_torch)
        await agent.separate(dummy_audio_torch)

        assert mock_predict.separate.call_count == 2
        for call in mock_predict.separate.call_args_list:
            assert call.kwargs.get("separator") is agent._model
            assert "model_str_or_path" not in call.kwargs


class TestOpenUnmixAgentSources:
    def test_sources_always_returns_known_stems(self, agent: OpenUnmixAgent) -> None:
        assert agent.sources == ["vocals", "drums", "bass", "other"]
