"""Unit tests for engine.demucs.separator — state machine, lazy imports."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from engine.audio.errors import AudioFileNotFoundError, AudioFormatError
from engine.demucs.config import SeparationConfig
from engine.demucs.errors import (
    InvalidAudioError,
    ModelLoadError,
    ProcessingError,
    SeparationError,
)
from engine.demucs.separator import DemucsSeparator, SeparationState

_INIT_PATCHES = [
    patch("engine.audio.preprocessor.AudioPreprocessor"),
    patch("engine.audio.postprocessor.AudioPostprocessor"),
    patch("engine.inference.model_manager.ModelManager"),
    patch("engine.inference.pipeline.InferencePipeline"),
    patch("engine.performance.optimizer.TorchRuntimeOptimizer"),
]


class TestSeparationState:
    def test_enum_values(self) -> None:
        assert SeparationState.IDLE == "idle"
        assert SeparationState.LOADING == "loading"
        assert SeparationState.PROCESSING == "processing"
        assert SeparationState.COMPLETE == "complete"
        assert SeparationState.ERROR == "error"

    def test_all_states_exist(self) -> None:
        assert len(SeparationState) == 6


class TestDemucsSeparatorInit:
    def test_initial_state(self) -> None:
        sep = DemucsSeparator(SeparationConfig())
        assert sep.state == SeparationState.IDLE
        assert sep.error is None

    def test_progress_callback_stored(self) -> None:
        cb = MagicMock()
        sep = DemucsSeparator(SeparationConfig(), progress_callback=cb)
        sep._report_progress(50)
        cb.assert_called_once_with(50)

    def test_progress_clamped_to_0_100(self) -> None:
        cb = MagicMock()
        sep = DemucsSeparator(SeparationConfig(), progress_callback=cb)
        sep._report_progress(150)
        cb.assert_called_once_with(100)

    def test_progress_clamped_negative(self) -> None:
        cb = MagicMock()
        sep = DemucsSeparator(SeparationConfig(), progress_callback=cb)
        sep._report_progress(-10)
        cb.assert_called_once_with(0)


class TestDemucsSeparatorInitialize:
    @pytest.mark.asyncio
    async def test_initialize_success_state_not_error(self) -> None:
        with (
            patch("engine.audio.preprocessor.AudioPreprocessor"),
            patch("engine.audio.postprocessor.AudioPostprocessor"),
            patch("engine.inference.model_manager.ModelManager") as mock_mm,
            patch("engine.inference.pipeline.InferencePipeline"),
            patch("engine.performance.optimizer.TorchRuntimeOptimizer"),
        ):
            mock_mm.return_value.switch_model = AsyncMock()
            sep = DemucsSeparator(SeparationConfig())
            await sep.initialize()
            assert sep.state != SeparationState.ERROR
            assert sep.state != SeparationState.COMPLETE
            assert sep.error is None

    @pytest.mark.asyncio
    async def test_initialize_calls_switch_model(self) -> None:
        with (
            patch("engine.audio.preprocessor.AudioPreprocessor"),
            patch("engine.audio.postprocessor.AudioPostprocessor"),
            patch("engine.inference.model_manager.ModelManager") as mock_mm,
            patch("engine.inference.pipeline.InferencePipeline"),
            patch("engine.performance.optimizer.TorchRuntimeOptimizer"),
        ):
            mock_mm.return_value.switch_model = AsyncMock()
            sep = DemucsSeparator(SeparationConfig())
            await sep.initialize()
            mock_mm.return_value.switch_model.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_initialize_sets_progress_to_20(self) -> None:
        cb = MagicMock()
        with (
            patch("engine.audio.preprocessor.AudioPreprocessor"),
            patch("engine.audio.postprocessor.AudioPostprocessor"),
            patch("engine.inference.model_manager.ModelManager") as mock_mm,
            patch("engine.inference.pipeline.InferencePipeline"),
            patch("engine.performance.optimizer.TorchRuntimeOptimizer"),
        ):
            mock_mm.return_value.switch_model = AsyncMock()
            sep = DemucsSeparator(SeparationConfig(), progress_callback=cb)
            await sep.initialize()
            calls = [c.args[0] for c in cb.call_args_list]
            assert 5 in calls
            assert 20 in calls

    @pytest.mark.asyncio
    async def test_initialize_error_sets_state_error(self) -> None:
        with (
            patch("engine.audio.preprocessor.AudioPreprocessor"),
            patch("engine.audio.postprocessor.AudioPostprocessor"),
            patch("engine.inference.model_manager.ModelManager") as mock_mm,
            patch("engine.inference.pipeline.InferencePipeline"),
            patch("engine.performance.optimizer.TorchRuntimeOptimizer"),
        ):
            mock_mm.return_value.switch_model = AsyncMock(
                side_effect=ModelLoadError("boom")
            )
            sep = DemucsSeparator(SeparationConfig())
            with pytest.raises(ModelLoadError):
                await sep.initialize()
            assert sep.state == SeparationState.ERROR
            assert sep.error is not None

    @pytest.mark.asyncio
    async def test_initialize_generic_error_wraps_model_load_error(self) -> None:
        with (
            patch("engine.audio.preprocessor.AudioPreprocessor"),
            patch("engine.audio.postprocessor.AudioPostprocessor"),
            patch("engine.inference.model_manager.ModelManager") as mock_mm,
            patch("engine.inference.pipeline.InferencePipeline"),
            patch("engine.performance.optimizer.TorchRuntimeOptimizer"),
        ):
            mock_mm.return_value.switch_model = AsyncMock(
                side_effect=RuntimeError("something broke")
            )
            sep = DemucsSeparator(SeparationConfig())
            with pytest.raises(ModelLoadError, match="Cannot initialize"):
                await sep.initialize()
            assert sep.state == SeparationState.ERROR


class TestDemucsSeparatorSeparate:
    @pytest.fixture
    def initialized_sep(self) -> DemucsSeparator:
        sep = DemucsSeparator(SeparationConfig())
        sep._pipeline = MagicMock()
        sep._preprocessor = MagicMock()
        sep._preprocessor.preprocess = AsyncMock(
            return_value=np.zeros(44100, dtype=np.float32)
        )
        sep._postprocessor = MagicMock()
        sep._postprocessor.postprocess = AsyncMock(
            return_value=np.zeros(44100, dtype=np.float32)
        )
        sep._pipeline.run = AsyncMock(
            return_value={
                "vocals": np.zeros(44100, dtype=np.float32),
                "drums": np.zeros(44100, dtype=np.float32),
            }
        )
        sep._state = SeparationState.IDLE
        return sep

    @pytest.mark.asyncio
    async def test_separate_not_initialized(self) -> None:
        sep = DemucsSeparator(SeparationConfig())
        with pytest.raises(SeparationError, match="not initialized"):
            await sep.separate(np.zeros(44100, dtype=np.float32))

    @pytest.mark.asyncio
    async def test_separate_empty_audio(self, initialized_sep: DemucsSeparator) -> None:
        with pytest.raises(InvalidAudioError, match="empty"):
            await initialized_sep.separate(np.array([], dtype=np.float32))

    @pytest.mark.asyncio
    async def test_separate_none_audio(self, initialized_sep: DemucsSeparator) -> None:
        with pytest.raises(InvalidAudioError):
            await initialized_sep.separate(None)  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_separate_3d_audio_rejected(
        self, initialized_sep: DemucsSeparator
    ) -> None:
        with pytest.raises(InvalidAudioError, match="3D"):
            await initialized_sep.separate(np.zeros((2, 2, 44100), dtype=np.float32))

    @pytest.mark.asyncio
    async def test_separate_1d_audio_accepted(
        self, initialized_sep: DemucsSeparator
    ) -> None:
        result = await initialized_sep.separate(np.zeros(44100, dtype=np.float32))
        assert "vocals" in result
        assert "drums" in result

    @pytest.mark.asyncio
    async def test_separate_2d_audio_accepted(
        self, initialized_sep: DemucsSeparator
    ) -> None:
        result = await initialized_sep.separate(np.zeros((2, 44100), dtype=np.float32))
        assert "vocals" in result

    @pytest.mark.asyncio
    async def test_separate_calls_preprocess(
        self, initialized_sep: DemucsSeparator
    ) -> None:
        audio = np.zeros(44100, dtype=np.float32)
        await initialized_sep.separate(audio, sample_rate=22050)
        initialized_sep._preprocessor.preprocess.assert_awaited_once_with(
            audio, 22050, normalize=True
        )

    @pytest.mark.asyncio
    async def test_separate_calls_pipeline_run(
        self, initialized_sep: DemucsSeparator
    ) -> None:
        await initialized_sep.separate(np.zeros(44100, dtype=np.float32))
        initialized_sep._pipeline.run.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_separate_sets_complete(
        self, initialized_sep: DemucsSeparator
    ) -> None:
        await initialized_sep.separate(np.zeros(44100, dtype=np.float32))
        assert initialized_sep.state == SeparationState.COMPLETE

    @pytest.mark.asyncio
    async def test_separate_error_sets_error_state(self) -> None:
        sep = DemucsSeparator(SeparationConfig())
        sep._pipeline = MagicMock()
        sep._preprocessor = MagicMock()
        sep._preprocessor.preprocess = AsyncMock(side_effect=Exception("crash"))
        sep._postprocessor = MagicMock()
        sep._state = SeparationState.IDLE
        with pytest.raises(ProcessingError):
            await sep.separate(np.zeros(44100, dtype=np.float32))
        assert sep.state == SeparationState.ERROR

    @pytest.mark.asyncio
    async def test_separate_returns_all_stems(
        self, initialized_sep: DemucsSeparator
    ) -> None:
        result = await initialized_sep.separate(np.zeros(44100, dtype=np.float32))
        assert set(result.keys()) == {"vocals", "drums"}


class TestDemucsSeparatorSeparateFile:
    @pytest.mark.asyncio
    async def test_separate_file_missing_raises(self, tmp_path: Path) -> None:
        sep = DemucsSeparator(SeparationConfig())
        sep._pipeline = MagicMock()
        sep._preprocessor = MagicMock()
        sep._preprocessor.preprocess = AsyncMock(
            return_value=np.zeros(44100, dtype=np.float32)
        )
        sep._postprocessor = MagicMock()
        sep._postprocessor.postprocess = AsyncMock(
            return_value=np.zeros(44100, dtype=np.float32)
        )
        sep._pipeline.run = AsyncMock(
            return_value={"vocals": np.zeros(44100, dtype=np.float32)}
        )
        with pytest.raises(AudioFileNotFoundError):
            await sep.separate_file(tmp_path / "nonexistent.wav")

    @pytest.mark.asyncio
    async def test_separate_file_unsupported_format(self, tmp_path: Path) -> None:
        sep = DemucsSeparator(SeparationConfig())
        f = tmp_path / "test.xyz"
        f.write_bytes(b"\x00" * 100)
        with pytest.raises(AudioFormatError):
            await sep.separate_file(f)


class TestDemucsSeparatorProgress:
    @pytest.mark.asyncio
    async def test_separate_emits_progress(self) -> None:
        cb = MagicMock()
        sep = DemucsSeparator(SeparationConfig(), progress_callback=cb)
        sep._pipeline = MagicMock()
        sep._preprocessor = MagicMock()
        sep._preprocessor.preprocess = AsyncMock(
            return_value=np.zeros(44100, dtype=np.float32)
        )
        sep._postprocessor = MagicMock()
        sep._postprocessor.postprocess = AsyncMock(
            return_value=np.zeros(44100, dtype=np.float32)
        )
        sep._pipeline.run = AsyncMock(
            return_value={"vocals": np.zeros(44100, dtype=np.float32)}
        )
        await sep.separate(np.zeros(44100, dtype=np.float32))
        calls = [c.args[0] for c in cb.call_args_list]
        assert 25 in calls
        assert 40 in calls
        assert 75 in calls
        assert 100 in calls


class TestDemucsSeparatorBuildInferenceConfig:
    def test_builds_config_from_separation_config(self) -> None:
        cfg = SeparationConfig(
            shifts=3,
            overlap=0.5,
            jobs=2,
            mixed_precision=True,
        )
        sep = DemucsSeparator(cfg)
        inf = sep._build_inference_config()
        assert inf.shifts == 3
        assert inf.overlap == 0.5
        assert inf.jobs == 2
        assert inf.mixed_precision is True
