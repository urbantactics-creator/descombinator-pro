"""Integration tests for the full audio separation pipeline."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest
import torch

from engine.audio.loader import AudioLoader
from engine.export.writer import ExportWriter
from engine.inference.model_manager import ModelManager
from engine.inference.pipeline import InferencePipeline


@pytest.fixture
def mock_model() -> MagicMock:
    """Mock separation model that returns deterministic stems."""
    model = MagicMock()
    model.separate = AsyncMock(
        return_value={
            "vocals": torch.randn(2, 44100),
            "other": torch.randn(2, 44100),
        }
    )
    model.sources = ["vocals", "other"]
    return model


@pytest.fixture
def mock_model_manager(mock_model: MagicMock) -> MagicMock:
    """Mock ModelManager with a pre-loaded model."""
    manager = MagicMock(spec=ModelManager)
    manager.current_model = mock_model
    manager.switch_model = AsyncMock(return_value=mock_model)
    return manager


@pytest.fixture
def pipeline(mock_model_manager: MagicMock) -> InferencePipeline:
    return InferencePipeline(mock_model_manager)


@pytest.fixture
def loader() -> AudioLoader:
    return AudioLoader()


@pytest.fixture
def writer() -> ExportWriter:
    return ExportWriter()


class TestFullPipeline:
    """End-to-end: AudioLoader -> InferencePipeline -> ExportWriter."""

    @pytest.mark.asyncio
    async def test_full_pipeline_mono(
        self,
        loader: AudioLoader,
        pipeline: InferencePipeline,
        writer: ExportWriter,
        sample_wav_path: Path,
        tmp_path: Path,
    ) -> None:
        audio = await loader.load(sample_wav_path, sr=44100, mono=True)
        assert audio.ndim == 1
        assert len(audio) == 44100 * 3

        stems = await pipeline.run(audio, 44100)
        assert "vocals" in stems
        assert "other" in stems
        assert isinstance(stems["vocals"], np.ndarray)

        output_paths = await writer.write(stems, tmp_path, sample_rate=44100)
        assert "vocals" in output_paths
        assert "other" in output_paths
        assert output_paths["vocals"].exists()
        assert output_paths["other"].exists()

    @pytest.mark.asyncio
    async def test_full_pipeline_stereo(
        self,
        loader: AudioLoader,
        pipeline: InferencePipeline,
        writer: ExportWriter,
        sample_stereo_path: Path,
        tmp_path: Path,
    ) -> None:
        import soundfile as sf

        audio = await loader.load(sample_stereo_path, sr=44100, mono=False)
        assert audio.ndim == 2
        assert audio.shape[0] == 2

        stems = await pipeline.run(audio, 44100)
        assert "vocals" in stems
        assert "other" in stems

        output_paths = await writer.write(stems, tmp_path, sample_rate=44100)
        assert output_paths["vocals"].exists()
        assert output_paths["other"].exists()

        # Regression: channels-first (2, N) stems must be exported as
        # frames-first (N, 2) files, not corrupt 2-frame WAVs.
        for stem_name, path in output_paths.items():
            data, sr = sf.read(str(path))
            assert sr == 44100
            assert data.ndim == 2
            assert data.shape == (stems[stem_name].shape[1], 2)
            assert data.shape[0] > 100

    @pytest.mark.asyncio
    async def test_full_pipeline_custom_sr(
        self,
        loader: AudioLoader,
        pipeline: InferencePipeline,
        writer: ExportWriter,
        sample_wav_path: Path,
        tmp_path: Path,
    ) -> None:
        audio = await loader.load(sample_wav_path, sr=22050, mono=True)
        assert len(audio) == 22050 * 3

        stems = await pipeline.run(audio, 22050)
        assert "vocals" in stems

        output_paths = await writer.write(stems, tmp_path, sample_rate=22050)
        assert output_paths["vocals"].exists()

    @pytest.mark.asyncio
    async def test_full_pipeline_output_format(
        self,
        loader: AudioLoader,
        pipeline: InferencePipeline,
        writer: ExportWriter,
        sample_wav_path: Path,
        tmp_path: Path,
    ) -> None:
        audio = await loader.load(sample_wav_path, sr=44100, mono=True)
        stems = await pipeline.run(audio, 44100)

        output_paths = await writer.write(stems, tmp_path, sample_rate=44100)
        for path in output_paths.values():
            assert path.suffix == ".wav"
            assert path.stat().st_size > 0

    @pytest.mark.asyncio
    async def test_full_pipeline_preserves_stem_names(
        self,
        loader: AudioLoader,
        pipeline: InferencePipeline,
        writer: ExportWriter,
        sample_wav_path: Path,
        tmp_path: Path,
    ) -> None:
        audio = await loader.load(sample_wav_path, sr=44100, mono=True)
        stems = await pipeline.run(audio, 44100)

        output_paths = await writer.write(stems, tmp_path, sample_rate=44100)
        for stem_name, path in output_paths.items():
            assert path.stem == stem_name

    @pytest.mark.asyncio
    async def test_full_pipeline_with_model_override(
        self,
        loader: AudioLoader,
        pipeline: InferencePipeline,
        writer: ExportWriter,
        sample_wav_path: Path,
        tmp_path: Path,
        mock_model: MagicMock,
    ) -> None:
        audio = await loader.load(sample_wav_path, sr=44100, mono=True)

        stems = await pipeline.run(audio, 44100, model_name="umxhq")
        assert "vocals" in stems

        output_paths = await writer.write(stems, tmp_path, sample_rate=44100)
        assert output_paths["vocals"].exists()

    @pytest.mark.asyncio
    async def test_full_pipeline_error_propagation(
        self,
        loader: AudioLoader,
        pipeline: InferencePipeline,
        writer: ExportWriter,
        tmp_path: Path,
    ) -> None:
        from engine.inference.errors import InferenceError

        pipeline._model_manager.current_model = None
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100)).astype(np.float32)

        with pytest.raises(InferenceError, match="No model loaded"):
            await pipeline.run(audio, 44100)
