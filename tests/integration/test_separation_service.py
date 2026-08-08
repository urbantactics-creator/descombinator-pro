"""Integration tests for SeparationService with mocked engine."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from app.services.separation_service import SeparationService
from engine.demucs.config import SeparationConfig
from engine.demucs.errors import InvalidAudioError, ProcessingError, SeparationError
from engine.demucs.separator import SeparationState


@pytest.fixture
def separation_config() -> SeparationConfig:
    return SeparationConfig()


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
    separator.initialize = AsyncMock()
    return separator


@pytest.fixture
def service(separation_config: SeparationConfig) -> SeparationService:
    return SeparationService(separation_config)


class TestSeparationService:
    """Integration tests for SeparationService."""

    @pytest.mark.asyncio
    async def test_separate_success(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
        sample_wav_path: Path,
    ) -> None:
        with patch.object(service, "_separator", mock_separator):
            result = await service.separate(sample_wav_path)

        assert "vocals" in result
        assert "other" in result
        assert isinstance(result["vocals"], np.ndarray)
        mock_separator.separate_file.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_separate_with_progress_callback(
        self,
        service: SeparationService,
        sample_wav_path: Path,
    ) -> None:
        progress_calls: list[tuple[int, str]] = []

        def callback(percent: int, message: str) -> None:
            progress_calls.append((percent, message))

        with patch("engine.demucs.separator.DemucsSeparator") as MockSeparator:
            mock_sep = MagicMock()
            mock_sep.initialize = AsyncMock()
            mock_sep.separate_file = AsyncMock(
                return_value={"vocals": np.zeros(44100, dtype=np.float32)}
            )
            MockSeparator.return_value = mock_sep

            await service.separate(sample_wav_path, progress_callback=callback)

            assert MockSeparator.call_count == 1
            _, kwargs = MockSeparator.call_args
            assert kwargs.get("progress_callback") is not None

    @pytest.mark.asyncio
    async def test_separate_initializes_separator(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
        sample_wav_path: Path,
    ) -> None:
        with patch(
            "engine.demucs.separator.DemucsSeparator",
            return_value=mock_separator,
        ):
            result = await service.separate(sample_wav_path)

        assert "vocals" in result
        mock_separator.initialize.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_separate_invalid_audio_error(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
        sample_wav_path: Path,
    ) -> None:
        mock_separator.separate_file = AsyncMock(
            side_effect=InvalidAudioError("Invalid audio")
        )

        with (
            patch.object(service, "_separator", mock_separator),
            pytest.raises(InvalidAudioError),
        ):
            await service.separate(sample_wav_path)

    @pytest.mark.asyncio
    async def test_separate_separation_error_wrapped(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
        sample_wav_path: Path,
    ) -> None:
        mock_separator.separate_file = AsyncMock(
            side_effect=SeparationError("Model failed")
        )

        with (
            patch.object(service, "_separator", mock_separator),
            pytest.raises(ProcessingError, match="Separation pipeline failed"),
        ):
            await service.separate(sample_wav_path)

    @pytest.mark.asyncio
    async def test_separate_missing_file(
        self,
        service: SeparationService,
    ) -> None:
        with patch("engine.demucs.separator.DemucsSeparator") as MockSeparator:
            mock_sep = MagicMock()
            mock_sep.initialize = AsyncMock()
            mock_sep.separate_file = AsyncMock(
                side_effect=FileNotFoundError("not found")
            )
            MockSeparator.return_value = mock_sep

            with pytest.raises((FileNotFoundError, Exception)):
                await service.separate(Path("nonexistent.wav"))

    @pytest.mark.asyncio
    async def test_initialize_creates_separator(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
    ) -> None:
        with patch(
            "engine.demucs.separator.DemucsSeparator",
            return_value=mock_separator,
        ):
            await service.initialize()

        assert service._separator is not None
        mock_separator.initialize.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_initialize_idempotent(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
    ) -> None:
        with patch(
            "engine.demucs.separator.DemucsSeparator",
            return_value=mock_separator,
        ):
            await service.initialize()
            await service.initialize()

        mock_separator.initialize.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_separate_returns_correct_stems(
        self,
        service: SeparationService,
        mock_separator: MagicMock,
        sample_wav_path: Path,
    ) -> None:
        expected_stems = {
            "vocals": np.ones(44100, dtype=np.float32),
            "drums": np.zeros(44100, dtype=np.float32),
            "bass": np.ones(44100, dtype=np.float32) * 0.5,
            "other": np.ones(44100, dtype=np.float32) * 0.3,
        }
        mock_separator.separate_file = AsyncMock(return_value=expected_stems)

        with patch.object(service, "_separator", mock_separator):
            result = await service.separate(sample_wav_path)

        assert set(result.keys()) == {"vocals", "drums", "bass", "other"}
        np.testing.assert_array_equal(result["vocals"], expected_stems["vocals"])
