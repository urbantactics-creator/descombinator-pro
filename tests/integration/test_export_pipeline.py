"""Integration tests for BatchExporter with real files."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from engine.export.batch_exporter import BatchExporter
from engine.export.config import ExportConfig, ExportFormat


@pytest.fixture
def batch_exporter() -> BatchExporter:
    """Return a WAV batch exporter."""
    return BatchExporter(ExportConfig(format=ExportFormat.WAV))


@pytest.fixture
def sample_stems() -> dict[str, np.ndarray]:
    """Generate sample stems for testing."""
    sr = 44100
    t = np.linspace(0, 1, sr)
    return {
        "vocals": (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32),
        "other": (np.sin(2 * np.pi * 880 * t) * 0.3).astype(np.float32),
    }


class TestBatchExporter:
    """Integration tests for BatchExporter."""

    @pytest.mark.asyncio
    async def test_export_all_writes_files(
        self,
        batch_exporter: BatchExporter,
        sample_stems: dict[str, np.ndarray],
        tmp_path: Path,
    ) -> None:
        """Exporting all stems creates real readable files."""
        results = await batch_exporter.export_all(sample_stems, tmp_path)

        assert len(results) == 2
        for path in results:
            assert path.exists()
            assert path.stat().st_size > 0

    @pytest.mark.asyncio
    async def test_export_all_preserves_stem_names(
        self,
        batch_exporter: BatchExporter,
        sample_stems: dict[str, np.ndarray],
        tmp_path: Path,
    ) -> None:
        """Exported file stems match the input stem names."""
        results = await batch_exporter.export_all(sample_stems, tmp_path)

        assert {p.stem for p in results} == set(sample_stems)

    @pytest.mark.asyncio
    async def test_export_all_flac_format(
        self,
        sample_stems: dict[str, np.ndarray],
        tmp_path: Path,
    ) -> None:
        """FLAC format is honored per file."""
        exporter = BatchExporter(ExportConfig(format=ExportFormat.FLAC))
        results = await exporter.export_all(sample_stems, tmp_path)

        assert len(results) == 2
        for path in results:
            assert path.suffix == ".flac"
            assert path.exists()

    @pytest.mark.asyncio
    async def test_export_all_mp3_format(
        self,
        sample_stems: dict[str, np.ndarray],
        tmp_path: Path,
    ) -> None:
        """MP3 format is honored per file."""
        exporter = BatchExporter(ExportConfig(format=ExportFormat.MP3))
        results = await exporter.export_all(sample_stems, tmp_path)

        assert len(results) == 2
        for path in results:
            assert path.suffix == ".mp3"
            assert path.exists()

    @pytest.mark.asyncio
    async def test_export_all_empty_results(
        self,
        batch_exporter: BatchExporter,
        tmp_path: Path,
    ) -> None:
        """Empty input produces no output files."""
        results = await batch_exporter.export_all({}, tmp_path)

        assert results == []

    @pytest.mark.asyncio
    async def test_export_all_single_file(
        self,
        batch_exporter: BatchExporter,
        sample_stems: dict[str, np.ndarray],
        tmp_path: Path,
    ) -> None:
        """A single stem is exported without errors."""
        results = await batch_exporter.export_all(
            {"vocals": sample_stems["vocals"]}, tmp_path
        )

        assert len(results) == 1
        assert results[0].exists()

    @pytest.mark.asyncio
    async def test_export_all_writes_readable_audio(
        self,
        batch_exporter: BatchExporter,
        sample_stems: dict[str, np.ndarray],
        tmp_path: Path,
    ) -> None:
        """Exported files are decodable at the expected sample rate."""
        results = await batch_exporter.export_all(sample_stems, tmp_path)

        for path in results:
            audio, sr = sf.read(str(path))
            assert sr == 44100
            assert len(audio) > 0

    @pytest.mark.asyncio
    async def test_export_all_creates_nested_dirs(
        self,
        batch_exporter: BatchExporter,
        sample_stems: dict[str, np.ndarray],
        tmp_path: Path,
    ) -> None:
        """Nested output directories are created on demand."""
        nested = tmp_path / "nested" / "output"
        results = await batch_exporter.export_all(sample_stems, nested)

        assert nested.is_dir()
        for path in results:
            assert path.exists()
