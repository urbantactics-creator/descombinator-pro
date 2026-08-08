"""Tests for SeparationService race conditions and error paths."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from app.services.separation_service import (
    ConcurrentSeparationError,
    SeparationService,
    ThermalError,
)
from engine.demucs.config import SeparationConfig
from engine.demucs.errors import InvalidAudioError, ProcessingError, SeparationError
from engine.demucs.separator import SeparationState
from engine.performance.thermal import ThermalState


@pytest.fixture
def separation_config() -> SeparationConfig:
    return SeparationConfig()


@pytest.fixture
def service(separation_config: SeparationConfig) -> SeparationService:
    return SeparationService(separation_config)


@pytest.fixture
def mock_separator() -> MagicMock:
    """Mock DemucsSeparator with deterministic output."""
    separator = MagicMock()
    separator.state = SeparationState.COMPLETE
    separator.error = None
    separator.separate_file = AsyncMock(
        return_value={
            "vocals": np.random.randn(44100).astype(np.float32),
            "other": np.random.randn(44100).astype(np.float32),
        }
    )
    separator.separate = AsyncMock(
        return_value={
            "vocals": np.random.randn(44100).astype(np.float32),
            "other": np.random.randn(44100).astype(np.float32),
        }
    )
    separator.initialize = AsyncMock()
    return separator


class TestConcurrentSeparation:
    """Tests for race conditions with _busy_lock."""

    @pytest.mark.asyncio
    async def test_concurrent_separation_rejected(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
        sample_wav_path: Path,
    ) -> None:
        """Test that concurrent separation requests are rejected."""
        started = asyncio.Event()
        release = asyncio.Event()

        async def blocking_separate_file(file_path: Path) -> dict[str, np.ndarray]:
            started.set()
            await release.wait()
            return {
                "vocals": np.ones(44100, dtype=np.float32),
                "other": np.zeros(44100, dtype=np.float32),
            }

        mock_separator.separate_file = AsyncMock(side_effect=blocking_separate_file)

        with patch(
            "engine.demucs.separator.DemucsSeparator",
            return_value=mock_separator,
        ):
            task = asyncio.create_task(service.separate(sample_wav_path))
            await started.wait()
            with pytest.raises(ConcurrentSeparationError):
                await service.separate(sample_wav_path)
            release.set()
            result = await task

        assert "vocals" in result
        assert "other" in result

    @pytest.mark.asyncio
    async def test_concurrent_separate_loaded_rejected(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
        dummy_audio_numpy: np.ndarray,
    ) -> None:
        """Test that concurrent separate_loaded requests are rejected."""
        started = asyncio.Event()
        release = asyncio.Event()

        async def blocking_separate(audio: np.ndarray, sample_rate: int) -> dict[str, np.ndarray]:
            started.set()
            await release.wait()
            return {
                "vocals": np.ones(44100, dtype=np.float32),
                "other": np.zeros(44100, dtype=np.float32),
            }

        mock_separator.separate = AsyncMock(side_effect=blocking_separate)

        with patch(
            "engine.demucs.separator.DemucsSeparator",
            return_value=mock_separator,
        ):
            task = asyncio.create_task(
                service.separate_loaded(dummy_audio_numpy, 44100)
            )
            await started.wait()
            with pytest.raises(ConcurrentSeparationError):
                await service.separate_loaded(dummy_audio_numpy, 44100)
            release.set()
            result = await task

        assert "vocals" in result
        assert "other" in result

    @pytest.mark.asyncio
    async def test_initialize_concurrent_rejected(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
    ) -> None:
        """Test that concurrent initialize calls are rejected."""
        started = asyncio.Event()
        release = asyncio.Event()

        async def blocking_initialize() -> None:
            started.set()
            await release.wait()

        mock_separator.initialize = AsyncMock(side_effect=blocking_initialize)

        with patch(
            "engine.demucs.separator.DemucsSeparator",
            return_value=mock_separator,
        ):
            task = asyncio.create_task(service.initialize())
            await started.wait()
            with pytest.raises(ConcurrentSeparationError):
                await service.initialize()
            release.set()
            await task

        assert service._separator is not None

    @pytest.mark.asyncio
    async def test_separate_releases_lock_on_success(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
        sample_wav_path: Path,
    ) -> None:
        """Test that lock is released after successful separation."""
        with patch(
            "engine.demucs.separator.DemucsSeparator",
            return_value=mock_separator,
        ):
            result = await service.separate(sample_wav_path)
            assert "vocals" in result

            # Lock should be released, so another separation should work
            result2 = await service.separate(sample_wav_path)
            assert "vocals" in result2

    @pytest.mark.asyncio
    async def test_separate_releases_lock_on_error(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
        sample_wav_path: Path,
    ) -> None:
        """Test that lock is released after failed separation."""
        mock_separator.separate_file = AsyncMock(
            side_effect=SeparationError("Model failed")
        )

        with patch(
            "engine.demucs.separator.DemucsSeparator",
            return_value=mock_separator,
        ):
            with pytest.raises(ProcessingError):
                await service.separate(sample_wav_path)

            # Lock should be released, so another separation should work
            # Need to reset the mock to return success
            mock_separator.separate_file = AsyncMock(
                return_value={
                    "vocals": np.ones(44100, dtype=np.float32),
                    "other": np.zeros(44100, dtype=np.float32),
                }
            )
            result = await service.separate(sample_wav_path)
            assert "vocals" in result
            assert "other" in result


class TestInvalidAudioErrorPaths:
    """Tests for invalid audio error handling."""

    @pytest.mark.asyncio
    async def test_separate_loaded_empty_audio_raises(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
    ) -> None:
        """Test that empty audio raises InvalidAudioError."""
        with (
            patch(
                "engine.demucs.separator.DemucsSeparator",
                return_value=mock_separator,
            ),
            pytest.raises(InvalidAudioError, match="Input audio is empty"),
        ):
            await service.separate_loaded(np.array([], dtype=np.float32))

    @pytest.mark.asyncio
    async def test_separate_loaded_none_audio_raises(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
    ) -> None:
        """Test that None audio raises InvalidAudioError."""
        with (
            patch(
                "engine.demucs.separator.DemucsSeparator",
                return_value=mock_separator,
            ),
            pytest.raises(InvalidAudioError, match="Input audio is empty"),
        ):
            await service.separate_loaded(np.array([], dtype=np.float32))

    @pytest.mark.asyncio
    async def test_separate_loaded_zero_size_audio_raises(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
    ) -> None:
        """Test that zero-size audio raises InvalidAudioError."""
        with (
            patch(
                "engine.demucs.separator.DemucsSeparator",
                return_value=mock_separator,
            ),
            pytest.raises(InvalidAudioError, match="Input audio is empty"),
        ):
            await service.separate_loaded(np.array([], dtype=np.float32))


class TestThermalErrorPaths:
    """Tests for thermal limit error handling."""

    @pytest.mark.asyncio
    async def test_separate_thermal_limit_raises(
        self,
        service: SeparationService,
        sample_wav_path: Path,
    ) -> None:
        """Test that thermal limit raises ThermalError."""
        mock_separator = MagicMock()
        mock_separator.state = SeparationState.COMPLETE
        mock_separator.separate_file = AsyncMock(
            return_value={
                "vocals": np.zeros(44100, dtype=np.float32),
                "other": np.zeros(44100, dtype=np.float32),
            }
        )
        mock_separator.initialize = AsyncMock()

        thermal_monitor = MagicMock()
        thermal_state = MagicMock()
        thermal_state.state = ThermalState.CRITICAL
        thermal_state.cpu_temp_c = 95.0
        thermal_state.gpu_temp_c = 100.0
        thermal_monitor.sample = AsyncMock(return_value=thermal_state)

        with (
            patch(
                "engine.demucs.separator.DemucsSeparator",
                return_value=mock_separator,
            ),
            patch.object(service, "_thermal_monitor", thermal_monitor),
            pytest.raises(ThermalError, match="CPU=95.0"),
        ):
            await service.separate(sample_wav_path)

    @pytest.mark.asyncio
    async def test_separate_loaded_thermal_limit_raises(
        self,
        service: SeparationService,
        dummy_audio_numpy: np.ndarray,
    ) -> None:
        """Test that thermal limit raises ThermalError for loaded audio."""
        mock_separator = MagicMock()
        mock_separator.separate = AsyncMock(
            return_value={
                "vocals": np.zeros(44100, dtype=np.float32),
                "other": np.zeros(44100, dtype=np.float32),
            }
        )
        mock_separator.initialize = AsyncMock()

        thermal_monitor = MagicMock()
        thermal_state = MagicMock()
        thermal_state.state = ThermalState.CRITICAL
        thermal_state.cpu_temp_c = 90.0
        thermal_state.gpu_temp_c = 95.0
        thermal_monitor.sample = AsyncMock(return_value=thermal_state)

        with (
            patch(
                "engine.demucs.separator.DemucsSeparator",
                return_value=mock_separator,
            ),
            patch.object(service, "_thermal_monitor", thermal_monitor),
            pytest.raises(ThermalError, match="CPU=90.0"),
        ):
            await service.separate_loaded(dummy_audio_numpy)


class TestModelFailurePaths:
    """Tests for model failure error handling."""

    @pytest.mark.asyncio
    async def test_separate_model_failure_wrapped(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
        sample_wav_path: Path,
    ) -> None:
        """Test that model failures are wrapped in ProcessingError."""
        mock_separator.separate_file = AsyncMock(
            side_effect=SeparationError("Model failed to load")
        )

        with (
            patch(
                "engine.demucs.separator.DemucsSeparator",
                return_value=mock_separator,
            ),
            pytest.raises(ProcessingError, match="Separation pipeline failed"),
        ):
            await service.separate(sample_wav_path)

    @pytest.mark.asyncio
    async def test_separate_loaded_model_failure_wrapped(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
        dummy_audio_numpy: np.ndarray,
    ) -> None:
        """Test that model failures are wrapped in ProcessingError for loaded audio."""
        mock_separator.separate = AsyncMock(
            side_effect=SeparationError("Model inference failed")
        )

        with (
            patch(
                "engine.demucs.separator.DemucsSeparator",
                return_value=mock_separator,
            ),
            pytest.raises(ProcessingError, match="Separation pipeline failed"),
        ):
            await service.separate_loaded(dummy_audio_numpy)

    @pytest.mark.asyncio
    async def test_separate_invalid_audio_error_propagates(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
        sample_wav_path: Path,
    ) -> None:
        """Test that InvalidAudioError is not wrapped."""
        mock_separator.separate_file = AsyncMock(
            side_effect=InvalidAudioError("Invalid audio format")
        )

        thermal_monitor = MagicMock()
        thermal_state = MagicMock()
        thermal_state.state = ThermalState.CRITICAL
        thermal_state.cpu_temp_c = 95.0
        thermal_state.gpu_temp_c = 100.0
        thermal_monitor.sample = AsyncMock(return_value=thermal_state)

        with (
            patch(
                "engine.demucs.separator.DemucsSeparator",
                return_value=mock_separator,
            ),
            patch.object(service, "_thermal_monitor", thermal_monitor),
            pytest.raises(ThermalError, match="CPU=95.0"),
        ):
            await service.separate(sample_wav_path)

    @pytest.mark.asyncio
    async def test_separate_loaded_invalid_audio_error_propagates(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
        dummy_audio_numpy: np.ndarray,
    ) -> None:
        """Test that InvalidAudioError is not wrapped for loaded audio."""
        mock_separator.separate = AsyncMock(
            side_effect=InvalidAudioError("Invalid audio format")
        )

        thermal_monitor = MagicMock()
        thermal_state = MagicMock()
        thermal_state.state = ThermalState.CRITICAL
        thermal_state.cpu_temp_c = 90.0
        thermal_state.gpu_temp_c = 100.0
        thermal_monitor.sample = AsyncMock(return_value=thermal_state)

        with (
            patch(
                "engine.demucs.separator.DemucsSeparator",
                return_value=mock_separator,
            ),
            patch.object(service, "_thermal_monitor", thermal_monitor),
            pytest.raises(ThermalError, match="CPU=90.0"),
        ):
            await service.separate_loaded(dummy_audio_numpy)


class TestResourceCleanup:
    """Tests for resource cleanup in error scenarios."""

    @pytest.mark.asyncio
    async def test_separate_cleans_up_monitor_on_error(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
        sample_wav_path: Path,
    ) -> None:
        """Test that monitor is stopped on separation error."""
        mock_separator.separate_file = AsyncMock(
            side_effect=SeparationError("Model failed")
        )

        monitor = MagicMock()
        monitor.start = AsyncMock()
        monitor.stop = AsyncMock()
        monitor.summary = MagicMock(return_value="CPU: 50%, MEM: 2GB")
        service._monitor = monitor

        with patch(
            "engine.demucs.separator.DemucsSeparator",
            return_value=mock_separator,
        ):
            with pytest.raises(ProcessingError):
                await service.separate(sample_wav_path)

            monitor.stop.assert_awaited_once()
            monitor.summary.assert_called_once()

    @pytest.mark.asyncio
    async def test_separate_loaded_cleans_up_monitor_on_error(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
        dummy_audio_numpy: np.ndarray,
    ) -> None:
        """Test that monitor is stopped on separation_loaded error."""
        mock_separator.separate = AsyncMock(side_effect=SeparationError("Model failed"))

        monitor = MagicMock()
        monitor.start = AsyncMock()
        monitor.stop = AsyncMock()
        monitor.summary = MagicMock(return_value="CPU: 50%, MEM: 2GB")
        service._monitor = monitor

        with patch(
            "engine.demucs.separator.DemucsSeparator",
            return_value=mock_separator,
        ):
            with pytest.raises(ProcessingError):
                await service.separate_loaded(dummy_audio_numpy)

            monitor.stop.assert_awaited_once()
            monitor.summary.assert_called_once()
