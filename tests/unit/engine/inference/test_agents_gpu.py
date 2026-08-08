"""GPU-related tests for inference agents and ModelManager.

All tests run on real CPU hardware; CUDA behavior is simulated by monkeypatching
``torch.cuda.is_available`` so the guarded code paths are exercised without a GPU.
"""

import gc
from unittest.mock import MagicMock, patch

import pytest
import torch

from engine.inference.config import DeviceType, InferenceConfig, ModelName
from engine.inference.demucs_agent import DemucsAgent
from engine.inference.errors import DeviceError
from engine.inference.model_manager import ModelManager
from engine.inference.openunmix_agent import OpenUnmixAgent


@pytest.fixture
def cuda_config() -> InferenceConfig:
    """Inference config targeting CUDA."""
    return InferenceConfig(
        model_name=ModelName.HTDEMUCS_FT,
        device=DeviceType.CUDA,
        mixed_precision=True,
        pin_memory=True,
    )


class TestDemucsAgentDeviceError:
    async def test_initialize_cuda_without_gpu_raises(
        self, cuda_config: InferenceConfig
    ) -> None:
        """DeviceError when CUDA requested but unavailable."""
        agent = DemucsAgent(cuda_config)
        with (
            patch("torch.cuda.is_available", return_value=False),
            pytest.raises(DeviceError, match="no GPU"),
        ):
            await agent.initialize()

    async def test_initialize_cuda_with_gpu_succeeds(
        self, cuda_config: InferenceConfig
    ) -> None:
        """With GPU present, initialize proceeds (Separator mocked)."""
        agent = DemucsAgent(cuda_config)
        mock_separator = MagicMock()
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch(
                "engine.inference.demucs_agent.Separator",
                create=True,
            ),
            patch("asyncio.to_thread", return_value=mock_separator),
        ):
            await agent.initialize()
            assert agent._separator is mock_separator

    async def test_separate_uses_autocast_and_pin_memory(
        self, cuda_config: InferenceConfig
    ) -> None:
        """autocast active with mixed_precision; pin_memory called on CPU tensor."""
        agent = DemucsAgent(cuda_config)
        mock_sep = MagicMock()
        stems_dict = {
            "vocals": torch.randn(2, 44100),
            "other": torch.randn(2, 44100),
        }
        mock_sep.separate_tensor.return_value = (None, stems_dict)
        agent._separator = mock_sep

        cpu_audio = torch.randn(2, 44100)
        pinned = MagicMock()
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.Stream", create=True),
            patch("torch.Tensor.pin_memory", return_value=pinned) as mock_pin,
            patch(
                "torch.autocast",
                return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()),
            ) as mock_autocast,
        ):
            result = await agent.separate(cpu_audio)

        mock_pin.assert_called_once()
        mock_autocast.assert_called_once_with(device_type="cuda", enabled=True)
        assert set(result) == {"vocals", "other"}

    async def test_separate_no_autocast_when_disabled(self) -> None:
        """Autocast disabled when mixed_precision is False."""
        config = InferenceConfig(
            model_name=ModelName.HTDEMUCS_FT,
            device=DeviceType.CUDA,
            mixed_precision=False,
        )
        agent = DemucsAgent(config)
        mock_sep = MagicMock()
        stems_dict = {
            "vocals": torch.randn(2, 44100),
            "other": torch.randn(2, 44100),
        }
        mock_sep.separate_tensor.return_value = (None, stems_dict)
        agent._separator = mock_sep

        with (
            patch("torch.cuda.is_available", return_value=True),
            patch(
                "torch.autocast",
                return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()),
            ) as mock_autocast,
        ):
            await agent.separate(torch.randn(2, 44100))

        mock_autocast.assert_called_once_with(device_type="cuda", enabled=False)


class TestOpenUnmixDeviceError:
    async def test_initialize_cuda_without_gpu_raises(
        self, cuda_config: InferenceConfig
    ) -> None:
        agent = OpenUnmixAgent(cuda_config)
        with (
            patch("torch.cuda.is_available", return_value=False),
            pytest.raises(DeviceError, match="no GPU"),
        ):
            await agent.initialize()

    async def test_separate_uses_autocast(self, cuda_config: InferenceConfig) -> None:
        agent = OpenUnmixAgent(cuda_config)
        agent._separator = MagicMock()
        stems_dict = {"vocals": torch.randn(1, 44100)}
        agent._separator.separate.return_value = stems_dict
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.Tensor.pin_memory", return_value=torch.randn(1, 44100)),
            patch(
                "torch.autocast",
                return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()),
            ) as mock_autocast,
        ):
            await agent.separate(torch.randn(1, 44100), sample_rate=44100)

        mock_autocast.assert_called_once_with(device_type="cuda", enabled=True)


class TestModelManagerMemory:
    async def test_free_memory_calls_empty_cache_and_gc(
        self, cuda_config: InferenceConfig, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """free_memory runs empty_cache (CUDA) then gc.collect()."""
        manager = ModelManager(cuda_config)
        calls: list[str] = []

        def fake_empty_cache() -> None:
            calls.append("empty_cache")

        def fake_gc_collect() -> None:
            calls.append("gc")

        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.empty_cache", side_effect=fake_empty_cache),
            patch.object(gc, "collect", side_effect=fake_gc_collect),
        ):
            manager.free_memory()

        assert calls == ["empty_cache", "gc"]

    async def test_free_memory_cpu_skips_empty_cache(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """On CPU, free_memory only runs gc.collect()."""
        manager = ModelManager(InferenceConfig(device=DeviceType.CPU))
        calls: list[str] = []

        def fake_gc_collect() -> None:
            calls.append("gc")

        with (
            patch("torch.cuda.empty_cache") as empty_cache,
            patch.object(gc, "collect", side_effect=fake_gc_collect),
        ):
            manager.free_memory()

        empty_cache.assert_not_called()
        assert calls == ["gc"]

    async def test_unload_all_clears_models(self) -> None:
        """unload_all removes every cached model and frees memory."""
        manager = ModelManager(InferenceConfig())
        model = MagicMock()
        manager._models = {name.value: model for name in ModelName}
        manager._current_name = ModelName.HTDEMUCS_FT.value

        with patch.object(manager, "free_memory") as free_memory:
            await manager.unload_all()

        assert manager._models == {}
        assert manager._current_name is None
        free_memory.assert_called_once()
