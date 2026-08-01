"""Unit tests for SeparationService separate_loaded and monitor integration."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from app.services.separation_service import SeparationService
from engine.demucs.config import SeparationConfig
from engine.demucs.errors import InvalidAudioError, ProcessingError, SeparationError
from engine.demucs.separator import SeparationState


@pytest.fixture
def config() -> SeparationConfig:
    return SeparationConfig()


@pytest.fixture
def mock_separator() -> MagicMock:
    """Mock DemucsSeparator with deterministic output."""
    separator = MagicMock()
    separator.state = SeparationState.COMPLETE
    separator.error = None
    separator.initialize = AsyncMock()
    separator.separate = AsyncMock(
        return_value={
            "vocals": np.ones(44100, dtype=np.float32),
            "other": np.zeros(44100, dtype=np.float32),
        }
    )
    separator.separate_file = AsyncMock(
        return_value={
            "vocals": np.ones(44100, dtype=np.float32),
            "other": np.zeros(44100, dtype=np.float32),
        }
    )
    return separator


@pytest.fixture
def sample_audio() -> np.ndarray:
    """Deterministic 1-second mono audio."""
    return np.linspace(-0.5, 0.5, 44100, dtype=np.float32)


def _make_monitor() -> MagicMock:
    """Build an AsyncMock-based ResourceMonitor stand-in."""
    monitor = MagicMock()
    monitor.start = AsyncMock()
    monitor.stop = AsyncMock()
    monitor.summary.return_value = "peak RSS=10.0 MB, samples=2, interval=1.0s"
    return monitor


class TestSeparateLoaded:
    """Tests for SeparationService.separate_loaded."""

    @pytest.mark.asyncio
    async def test_separate_loaded_reuses_audio(
        self,
        config: SeparationConfig,
        mock_separator: MagicMock,
        sample_audio: np.ndarray,
    ) -> None:
        """Pre-decoded audio goes to separator.separate, not separate_file."""
        service = SeparationService(config)
        with patch.object(service, "_separator", mock_separator):
            result = await service.separate_loaded(sample_audio, 44100)

        assert "vocals" in result
        assert "other" in result
        mock_separator.separate.assert_awaited_once_with(sample_audio, 44100)
        mock_separator.separate_file.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_separate_loaded_empty_audio_raises(
        self,
        config: SeparationConfig,
        mock_separator: MagicMock,
    ) -> None:
        """Empty audio raises InvalidAudioError before touching the separator."""
        service = SeparationService(config)
        with (
            patch.object(service, "_separator", mock_separator),
            pytest.raises(InvalidAudioError),
        ):
            await service.separate_loaded(np.array([], dtype=np.float32))

        mock_separator.separate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_separate_loaded_none_audio_raises(
        self,
        config: SeparationConfig,
        mock_separator: MagicMock,
    ) -> None:
        """None audio raises InvalidAudioError."""
        service = SeparationService(config)
        with (
            patch.object(service, "_separator", mock_separator),
            pytest.raises(InvalidAudioError),
        ):
            await service.separate_loaded(None, 44100)  # type: ignore[arg-type]

        mock_separator.separate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_separate_loaded_initializes_separator_lazily(
        self,
        config: SeparationConfig,
        sample_audio: np.ndarray,
    ) -> None:
        """Lazy-created separator via engine.demucs.separator.DemucsSeparator."""
        with patch("engine.demucs.separator.DemucsSeparator") as MockSeparator:
            mock_sep = MagicMock()
            mock_sep.initialize = AsyncMock()
            mock_sep.state = SeparationState.IDLE
            mock_sep.separate = AsyncMock(
                return_value={"vocals": np.ones(44100, dtype=np.float32)}
            )
            MockSeparator.return_value = mock_sep

            service = SeparationService(config)
            result = await service.separate_loaded(sample_audio, 44100)

        assert "vocals" in result
        MockSeparator.assert_called_once()
        mock_sep.initialize.assert_awaited_once()
        mock_sep.separate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_separate_loaded_separation_error_wrapped(
        self,
        config: SeparationConfig,
        mock_separator: MagicMock,
        sample_audio: np.ndarray,
    ) -> None:
        """SeparationError is wrapped as ProcessingError."""
        mock_separator.separate = AsyncMock(side_effect=SeparationError("Model failed"))
        service = SeparationService(config)
        with (
            patch.object(service, "_separator", mock_separator),
            pytest.raises(ProcessingError, match="Separation pipeline failed"),
        ):
            await service.separate_loaded(sample_audio, 44100)

    @pytest.mark.asyncio
    async def test_separate_loaded_invalid_audio_passthrough(
        self,
        config: SeparationConfig,
        mock_separator: MagicMock,
        sample_audio: np.ndarray,
    ) -> None:
        """InvalidAudioError from the separator is re-raised unchanged."""
        mock_separator.separate = AsyncMock(side_effect=InvalidAudioError("bad"))
        service = SeparationService(config)
        with (
            patch.object(service, "_separator", mock_separator),
            pytest.raises(InvalidAudioError),
        ):
            await service.separate_loaded(sample_audio, 44100)


class TestSeparateLoadedMonitor:
    """Tests for ResourceMonitor lifecycle around separate_loaded."""

    @pytest.mark.asyncio
    async def test_monitor_start_stop_around_separation(
        self,
        config: SeparationConfig,
        mock_separator: MagicMock,
        sample_audio: np.ndarray,
    ) -> None:
        """Monitor starts before and stops after separation, summary logged."""
        monitor = _make_monitor()
        service = SeparationService(config, monitor=monitor)
        with patch.object(service, "_separator", mock_separator):
            await service.separate_loaded(sample_audio, 44100)

        monitor.start.assert_awaited_once()
        monitor.stop.assert_awaited_once()
        monitor.summary.assert_called_once()
        assert service._monitor is monitor

    @pytest.mark.asyncio
    async def test_monitor_stop_called_on_error(
        self,
        config: SeparationConfig,
        mock_separator: MagicMock,
        sample_audio: np.ndarray,
    ) -> None:
        """Monitor stops even when separation raises."""
        mock_separator.separate = AsyncMock(side_effect=SeparationError("boom"))
        monitor = _make_monitor()
        service = SeparationService(config, monitor=monitor)
        with (
            patch.object(service, "_separator", mock_separator),
            pytest.raises(ProcessingError),
        ):
            await service.separate_loaded(sample_audio, 44100)

        monitor.start.assert_awaited_once()
        monitor.stop.assert_awaited_once()
        monitor.summary.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_monitor_no_crash(
        self,
        config: SeparationConfig,
        mock_separator: MagicMock,
        sample_audio: np.ndarray,
    ) -> None:
        """Service works without a monitor."""
        service = SeparationService(config)
        with patch.object(service, "_separator", mock_separator):
            result = await service.separate_loaded(sample_audio, 44100)

        assert "vocals" in result
