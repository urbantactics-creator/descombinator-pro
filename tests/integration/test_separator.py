"""Integration tests for DemucsSeparator."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from engine.demucs.config import SeparationConfig
from engine.demucs.errors import (
    InvalidAudioError,
    ModelLoadError,
    ProcessingError,
    SeparationError,
)
from engine.demucs.separator import DemucsSeparator, SeparationState


@pytest.fixture
def separator_config() -> SeparationConfig:
    return SeparationConfig(model_name="htdemucs_ft", device="cpu")


@pytest.fixture
def separator(separator_config: SeparationConfig) -> DemucsSeparator:
    return DemucsSeparator(separator_config)


class TestDemucsSeparatorInit:
    async def test_initial_state_is_idle(self, separator: DemucsSeparator) -> None:
        assert separator.state == SeparationState.IDLE

    async def test_error_is_none_initially(self, separator: DemucsSeparator) -> None:
        assert separator.error is None

    async def test_progress_callback_stored(
        self, separator_config: SeparationConfig
    ) -> None:
        callback = MagicMock()
        sep = DemucsSeparator(separator_config, progress_callback=callback)
        assert sep._progress_callback is callback


class TestDemucsSeparatorInitialize:
    async def test_initialize_sets_loading_then_idle_or_complete(
        self, separator: DemucsSeparator
    ) -> None:
        with (
            patch("engine.inference.model_manager.ModelManager") as MockManager,
            patch("engine.inference.pipeline.InferencePipeline") as MockPipeline,
        ):
            mock_manager = MagicMock()
            mock_manager.switch_model = AsyncMock()
            MockManager.return_value = mock_manager
            MockPipeline.return_value = MagicMock()

            await separator.initialize()

            assert separator.state in (
                SeparationState.LOADING,
                SeparationState.COMPLETE,
            )

    async def test_initialize_sets_error_on_failure(
        self, separator: DemucsSeparator
    ) -> None:
        with patch(
            "engine.inference.model_manager.ModelManager",
            side_effect=ModelLoadError("mock failure"),
        ):
            with pytest.raises(ModelLoadError):
                await separator.initialize()
            assert separator.state == SeparationState.ERROR
            assert isinstance(separator.error, ModelLoadError)


class TestDemucsSeparatorSeparate:
    async def test_separate_raises_if_not_initialized(
        self, separator: DemucsSeparator
    ) -> None:
        with pytest.raises(SeparationError):
            await separator.separate(np.zeros(44100, dtype=np.float32))

    async def test_separate_reports_progress(self, separator: DemucsSeparator) -> None:
        progress_values = []

        def track_progress(percent: int) -> None:
            progress_values.append(percent)

        sep = DemucsSeparator(
            SeparationConfig(model_name="htdemucs_ft"),
            progress_callback=track_progress,
        )

        with (
            patch("engine.inference.model_manager.ModelManager") as MockManager,
            patch("engine.inference.pipeline.InferencePipeline") as MockPipeline,
        ):
            mock_manager = MagicMock()
            mock_manager.switch_model = AsyncMock()
            MockManager.return_value = mock_manager

            mock_pipeline = MagicMock()
            mock_pipeline.run = AsyncMock(
                return_value={"vocals": np.zeros(44100, dtype=np.float32)}
            )
            MockPipeline.return_value = mock_pipeline

            await sep.initialize()
            await sep.separate(np.zeros(44100, dtype=np.float32))

            assert any(p >= 100 for p in progress_values)

    async def test_separate_empty_audio_raises(
        self, separator: DemucsSeparator
    ) -> None:
        with (
            patch("engine.inference.model_manager.ModelManager") as MockManager,
            patch("engine.inference.pipeline.InferencePipeline") as MockPipeline,
        ):
            mock_manager = MagicMock()
            mock_manager.switch_model = AsyncMock()
            MockManager.return_value = mock_manager
            MockPipeline.return_value = MagicMock()

            await separator.initialize()
            with pytest.raises(InvalidAudioError):
                await separator.separate(np.array([], dtype=np.float32))

    async def test_separate_invalid_ndim_raises(
        self, separator: DemucsSeparator
    ) -> None:
        with (
            patch("engine.inference.model_manager.ModelManager") as MockManager,
            patch("engine.inference.pipeline.InferencePipeline") as MockPipeline,
        ):
            mock_manager = MagicMock()
            mock_manager.switch_model = AsyncMock()
            MockManager.return_value = mock_manager
            MockPipeline.return_value = MagicMock()

            await separator.initialize()
            with pytest.raises(InvalidAudioError):
                await separator.separate(np.zeros((2, 3, 4), dtype=np.float32))

    async def test_separate_sets_complete_on_success(
        self, separator: DemucsSeparator
    ) -> None:
        with (
            patch("engine.inference.model_manager.ModelManager") as MockManager,
            patch("engine.inference.pipeline.InferencePipeline") as MockPipeline,
            patch("engine.audio.postprocessor.AudioPostprocessor") as MockPost,
        ):
            mock_manager = MagicMock()
            mock_manager.switch_model = AsyncMock()
            MockManager.return_value = mock_manager

            mock_pipeline = MagicMock()
            mock_pipeline.run = AsyncMock(
                return_value={"vocals": np.zeros(44100, dtype=np.float32)}
            )
            MockPipeline.return_value = mock_pipeline

            mock_post = MagicMock()
            mock_post.postprocess = AsyncMock(side_effect=lambda audio, sr: audio)
            MockPost.return_value = mock_post

            await separator.initialize()
            await separator.separate(np.zeros(44100, dtype=np.float32))
            assert separator.state == SeparationState.COMPLETE

    async def test_separate_sets_error_on_failure(
        self, separator: DemucsSeparator
    ) -> None:
        with (
            patch("engine.inference.model_manager.ModelManager") as MockManager,
            patch("engine.inference.pipeline.InferencePipeline") as MockPipeline,
        ):
            mock_manager = MagicMock()
            mock_manager.switch_model = AsyncMock()
            MockManager.return_value = mock_manager

            mock_pipeline = MagicMock()
            mock_pipeline.run = AsyncMock(side_effect=ProcessingError("mock"))
            MockPipeline.return_value = mock_pipeline

            await separator.initialize()
            with pytest.raises(ProcessingError):
                await separator.separate(np.zeros(44100, dtype=np.float32))
            assert separator.state == SeparationState.ERROR


class TestDemucsSeparatorSeparateFile:
    async def test_separate_file_loads_and_separates(
        self, separator: DemucsSeparator, tmp_path: Path
    ) -> None:
        import wave

        test_file = tmp_path / "test.wav"
        with wave.open(str(test_file), "w") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(44100)
            w.writeframes(np.zeros(44100, dtype=np.int16).tobytes())

        with (
            patch("engine.inference.model_manager.ModelManager") as MockManager,
            patch("engine.inference.pipeline.InferencePipeline") as MockPipeline,
            patch("engine.audio.postprocessor.AudioPostprocessor") as MockPost,
        ):
            mock_manager = MagicMock()
            mock_manager.switch_model = AsyncMock()
            MockManager.return_value = mock_manager

            mock_pipeline = MagicMock()
            mock_pipeline.run = AsyncMock(
                return_value={"vocals": np.zeros(44100, dtype=np.float32)}
            )
            MockPipeline.return_value = mock_pipeline

            mock_post = MagicMock()
            mock_post.postprocess = AsyncMock(side_effect=lambda audio, sr: audio)
            MockPost.return_value = mock_post

            await separator.initialize()
            result = await separator.separate_file(test_file)
            assert "vocals" in result
