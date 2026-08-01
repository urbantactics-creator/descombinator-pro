"""Tests for BatchExporter."""

from pathlib import Path

import numpy as np
import pytest

from engine.export.batch_exporter import BatchExporter
from engine.export.config import ExportConfig, ExportFormat


@pytest.fixture
def batch_exporter() -> BatchExporter:
    """Return a batch exporter."""
    config = ExportConfig(format=ExportFormat.WAV)
    return BatchExporter(config)


@pytest.fixture
def sample_stems_dict() -> dict[str, np.ndarray]:
    """Return a dict of sample stems."""
    return {
        "vocals": np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100)).astype(np.float32),
        "drums": np.sin(2 * np.pi * 220 * np.linspace(0, 1, 44100)).astype(np.float32),
        "bass": np.sin(2 * np.pi * 110 * np.linspace(0, 1, 44100)).astype(np.float32),
    }


class TestBatchExporter:
    async def test_export_all(
        self,
        batch_exporter: BatchExporter,
        sample_stems_dict: dict[str, np.ndarray],
        tmp_output_dir: Path,
    ) -> None:
        """Test exporting all stems sequentially."""
        results = await batch_exporter.export_all(sample_stems_dict, tmp_output_dir)

        assert len(results) == 3
        for path in results:
            assert path.exists()

    async def test_export_parallel(
        self,
        batch_exporter: BatchExporter,
        sample_stems_dict: dict[str, np.ndarray],
        tmp_output_dir: Path,
    ) -> None:
        """Test exporting stems in parallel."""
        results = await batch_exporter.export_parallel(
            sample_stems_dict, tmp_output_dir
        )

        assert len(results) == 3
        for path in results:
            assert path.exists()

    async def test_progress_callback(
        self,
        sample_stems_dict: dict[str, np.ndarray],
        tmp_output_dir: Path,
    ) -> None:
        """Test progress callback functionality."""
        progress_calls = []

        def progress_callback(current: int, total: int) -> None:
            progress_calls.append((current, total))

        config = ExportConfig(format=ExportFormat.WAV)
        exporter = BatchExporter(config, progress_callback)
        await exporter.export_all(sample_stems_dict, tmp_output_dir)

        assert len(progress_calls) == 3
        assert progress_calls[0] == (1, 3)
        assert progress_calls[-1] == (3, 3)

    async def test_error_handling(
        self,
        batch_exporter: BatchExporter,
        tmp_output_dir: Path,
    ) -> None:
        """Test error handling continues on failure."""
        good_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100)).astype(
            np.float32
        )
        stems = {
            "good": good_audio,
            "bad": np.array([1.0, 2.0, 3.0], dtype=np.float32),
        }

        results = await batch_exporter.export_all(stems, tmp_output_dir)

        # Both should succeed since clipping handles out-of-range values
        assert len(results) == 2
        for path in results:
            assert path.exists()

    async def test_concurrent_limit(
        self,
        batch_exporter: BatchExporter,
        sample_stems_dict: dict[str, np.ndarray],
        tmp_output_dir: Path,
    ) -> None:
        """Test concurrent export with limited concurrency."""
        results = await batch_exporter.export_parallel(
            sample_stems_dict, tmp_output_dir, max_concurrent=2
        )

        assert len(results) == 3
        for path in results:
            assert path.exists()
