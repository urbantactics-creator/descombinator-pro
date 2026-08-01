"""Integration tests for BatchExporter with real files."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from engine.export.batch_exporter import BatchExporter
from engine.export.config import ExportConfig, ExportFormat
from engine.export.writer import ExportWriter


@pytest.fixture
def writer() -> ExportWriter:
    return ExportWriter()


@pytest.fixture
def batch_exporter(writer: ExportWriter) -> BatchExporter:
    return BatchExporter(writer=writer)


@pytest.fixture
def sample_stems() -> dict[str, np.ndarray]:
    """Generate sample stems for testing."""
    sr = 44100
    t = np.linspace(0, 1, sr)
    return {
        "vocals": (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32),
        "other": (np.sin(2 * np.pi * 880 * t) * 0.3).astype(np.float32),
    }


@pytest.fixture
def batch_results(
    sample_stems: dict[str, np.ndarray],
) -> dict[str, dict[str, np.ndarray]]:
    """Generate batch results for multiple files."""
    return {
        "song1.wav": sample_stems,
        "song2.wav": sample_stems,
    }


class TestBatchExporter:
    """Integration tests for BatchExporter."""

    @pytest.mark.asyncio
    async def test_export_batch_creates_directories(
        self,
        batch_exporter: BatchExporter,
        batch_results: dict[str, dict[str, np.ndarray]],
        tmp_path: Path,
    ) -> None:
        output = await batch_exporter.export_batch(batch_results, tmp_path)

        assert "song1.wav" in output
        assert "song2.wav" in output
        assert (tmp_path / "song1").is_dir()
        assert (tmp_path / "song2").is_dir()

    @pytest.mark.asyncio
    async def test_export_batch_writes_files(
        self,
        batch_exporter: BatchExporter,
        batch_results: dict[str, dict[str, np.ndarray]],
        tmp_path: Path,
    ) -> None:
        output = await batch_exporter.export_batch(batch_results, tmp_path)

        for filename, stems in output.items():
            for stem_name, path in stems.items():
                assert path.exists()
                assert path.stat().st_size > 0

    @pytest.mark.asyncio
    async def test_export_batch_preserves_stem_names(
        self,
        batch_exporter: BatchExporter,
        batch_results: dict[str, dict[str, np.ndarray]],
        tmp_path: Path,
    ) -> None:
        output = await batch_exporter.export_batch(batch_results, tmp_path)

        for filename, stems in output.items():
            for stem_name, path in stems.items():
                assert path.stem == stem_name

    @pytest.mark.asyncio
    async def test_export_batch_flac_format(
        self,
        tmp_path: Path,
        batch_results: dict[str, dict[str, np.ndarray]],
    ) -> None:
        config = ExportConfig(format=ExportFormat.FLAC)
        writer = ExportWriter(config)
        exporter = BatchExporter(writer=writer)

        output = await exporter.export_batch(batch_results, tmp_path)

        for filename, stems in output.items():
            for stem_name, path in stems.items():
                assert path.suffix == ".flac"
                assert path.exists()

    @pytest.mark.asyncio
    async def test_export_batch_mp3_format(
        self,
        tmp_path: Path,
        batch_results: dict[str, dict[str, np.ndarray]],
    ) -> None:
        config = ExportConfig(format=ExportFormat.MP3)
        writer = ExportWriter(config)
        exporter = BatchExporter(writer=writer)

        output = await exporter.export_batch(batch_results, tmp_path)

        for filename, stems in output.items():
            for stem_name, path in stems.items():
                assert path.suffix == ".mp3"
                assert path.exists()

    @pytest.mark.asyncio
    async def test_export_batch_empty_results(
        self,
        batch_exporter: BatchExporter,
        tmp_path: Path,
    ) -> None:
        output = await batch_exporter.export_batch({}, tmp_path)
        assert output == {}

    @pytest.mark.asyncio
    async def test_export_batch_single_file(
        self,
        batch_exporter: BatchExporter,
        sample_stems: dict[str, np.ndarray],
        tmp_path: Path,
    ) -> None:
        results = {"single.wav": sample_stems}
        output = await batch_exporter.export_batch(results, tmp_path)

        assert "single.wav" in output
        assert (tmp_path / "single").is_dir()
        assert output["single.wav"]["vocals"].exists()

    @pytest.mark.asyncio
    async def test_export_batch_writes_readable_audio(
        self,
        batch_exporter: BatchExporter,
        batch_results: dict[str, dict[str, np.ndarray]],
        tmp_path: Path,
    ) -> None:
        output = await batch_exporter.export_batch(batch_results, tmp_path)

        for filename, stems in output.items():
            for stem_name, path in stems.items():
                audio, sr = sf.read(str(path))
                assert sr == 44100
                assert len(audio) > 0

    @pytest.mark.asyncio
    async def test_export_batch_creates_nested_dirs(
        self,
        batch_exporter: BatchExporter,
        batch_results: dict[str, dict[str, np.ndarray]],
        tmp_path: Path,
    ) -> None:
        nested = tmp_path / "nested" / "output"
        output = await batch_exporter.export_batch(batch_results, nested)

        assert nested.is_dir()
        for filename, stems in output.items():
            for path in stems.values():
                assert path.exists()
