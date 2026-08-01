"""Unit tests for DemucsAgent."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import torch

from engine.inference.config import InferenceConfig, ModelName
from engine.inference.demucs_agent import DemucsAgent
from engine.inference.errors import InferenceError, ModelLoadError


@pytest.fixture
def config() -> InferenceConfig:
    return InferenceConfig(model_name=ModelName.HTDEMUCS_FT)


@pytest.fixture
def agent(config: InferenceConfig) -> DemucsAgent:
    return DemucsAgent(config)


class TestDemucsAgentInit:
    def test_creates_without_error(self, agent: DemucsAgent) -> None:
        assert agent._separator is None
        assert agent.sources == []


class TestDemucsAgentInitialize:
    @pytest.mark.asyncio
    async def test_initialize_success(self, agent: DemucsAgent) -> None:
        mock_separator = MagicMock()
        mock_separator.model.sources = ["vocals", "drums", "bass", "other"]
        with (
            patch(
                "engine.inference.demucs_agent.Separator",
                create=True,
            ),
            patch("asyncio.to_thread", return_value=mock_separator),
        ):
            await agent.initialize()
            assert agent._separator is mock_separator

    @pytest.mark.asyncio
    async def test_initialize_import_error(self, agent: DemucsAgent) -> None:
        with (
            patch(
                "builtins.__import__",
                side_effect=ImportError("no demucs"),
            ),
            pytest.raises(ModelLoadError, match="Cannot load Demucs"),
        ):
            await agent.initialize()


class TestDemucsAgentSeparate:
    @pytest.mark.asyncio
    async def test_separate_before_init(
        self, agent: DemucsAgent, dummy_audio_torch: torch.Tensor
    ) -> None:
        with pytest.raises(InferenceError, match="not initialized"):
            await agent.separate(dummy_audio_torch)

    @pytest.mark.asyncio
    async def test_separate_returns_filtered_stems(
        self, agent: DemucsAgent, dummy_audio_torch: torch.Tensor
    ) -> None:
        vocals = torch.randn(2, 44100)
        other = torch.randn(2, 44100)
        drums = torch.randn(2, 44100)
        bass = torch.randn(2, 44100)
        stems_dict = {
            "vocals": vocals,
            "other": other,
            "drums": drums,
            "bass": bass,
        }
        mock_sep = MagicMock()
        mock_sep.separate_tensor.return_value = (dummy_audio_torch, stems_dict)
        agent._separator = mock_sep

        result = await agent.separate(dummy_audio_torch)

        assert "vocals" in result
        assert "other" in result
        assert "drums" not in result
        assert "bass" not in result

    @pytest.mark.asyncio
    async def test_separate_generic_error(
        self, agent: DemucsAgent, dummy_audio_torch: torch.Tensor
    ) -> None:
        mock_sep = MagicMock()
        mock_sep.separate_tensor.side_effect = RuntimeError("boom")
        agent._separator = mock_sep

        with pytest.raises(InferenceError, match="Separation failed"):
            await agent.separate(dummy_audio_torch)


class TestDemucsAgentSources:
    def test_sources_empty_when_not_init(self, agent: DemucsAgent) -> None:
        assert agent.sources == []

    def test_sources_returns_model_sources(self, agent: DemucsAgent) -> None:
        mock_sep = MagicMock()
        mock_sep.model.sources = ["vocals", "drums"]
        agent._separator = mock_sep
        assert agent.sources == ["vocals", "drums"]
