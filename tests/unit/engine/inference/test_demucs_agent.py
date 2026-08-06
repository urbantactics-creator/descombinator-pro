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
        import builtins

        real_import = builtins.__import__

        def fail_demucs(name: str, *args: object, **kwargs: object) -> object:
            if name == "demucs.api":
                raise ImportError("no demucs")
            return real_import(name, *args, **kwargs)

        with (
            patch("builtins.__import__", side_effect=fail_demucs),
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


class TestDemucsAgentMonoUpmix:
    """Mono inputs must be upmixed to stereo for stereo-only Demucs models."""

    def _make_mock(self, audio: torch.Tensor) -> MagicMock:
        """Build a mock separator returning filtered stems."""
        stems_dict = {
            "vocals": torch.randn(2, 44100),
            "other": torch.randn(2, 44100),
        }
        mock_sep = MagicMock()
        mock_sep.separate_tensor.return_value = (audio, stems_dict)
        return mock_sep

    @pytest.mark.asyncio
    async def test_separate_upmixes_single_channel_to_stereo(
        self, agent: DemucsAgent
    ) -> None:
        """A (1, N) mono tensor is duplicated to (2, N) before inference."""
        mono = torch.randn(1, 44100)
        mock_sep = self._make_mock(mono)
        agent._separator = mock_sep

        await agent.separate(mono)

        assert mock_sep.separate_tensor.call_count == 1
        called = mock_sep.separate_tensor.call_args.args[0]
        assert called.shape == (2, 44100)
        assert torch.equal(called[0], called[1])

    @pytest.mark.asyncio
    async def test_separate_upmixes_1d_input_to_stereo(
        self, agent: DemucsAgent
    ) -> None:
        """A raw (N,) tensor is reshaped and duplicated to (2, N)."""
        mono_1d = torch.randn(44100)
        mock_sep = self._make_mock(mono_1d)
        agent._separator = mock_sep

        await agent.separate(mono_1d)

        assert mock_sep.separate_tensor.call_count == 1
        called = mock_sep.separate_tensor.call_args.args[0]
        assert called.shape == (2, 44100)
        assert torch.equal(called[0], called[1])

    @pytest.mark.asyncio
    async def test_separate_leaves_stereo_unchanged(self, agent: DemucsAgent) -> None:
        """Genuine (2, N) stereo input is passed through untouched."""
        stereo = torch.randn(2, 44100)
        mock_sep = self._make_mock(stereo)
        agent._separator = mock_sep

        await agent.separate(stereo)

        assert mock_sep.separate_tensor.call_count == 1
        called = mock_sep.separate_tensor.call_args.args[0]
        assert called.shape == (2, 44100)
        assert called is stereo
