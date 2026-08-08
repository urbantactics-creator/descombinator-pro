"""Benchmarks for export writer and batch exporter."""

import asyncio
from pathlib import Path

import numpy as np
import pytest

from engine.export.batch_exporter import BatchExporter
from engine.export.config import ExportConfig, ExportFormat
from engine.export.writer import ExportWriter

_runner: asyncio.Runner | None = None


def _get_runner() -> asyncio.Runner:
    global _runner
    if _runner is None:
        _runner = asyncio.Runner()
    return _runner


def _run(coro) -> object:
    return _get_runner().run(coro)


@pytest.fixture
def tmp_export_dir(tmp_path: Path) -> Path:
    return tmp_path / "export"


def _stem_path(tmp_export_dir: Path, ext: str) -> Path:
    return tmp_export_dir / f"vocals.{ext}"


def test_bench_export_wav_1min(
    benchmark, tmp_export_dir: Path, synthetic_stems: dict[str, np.ndarray]
) -> None:
    """Export one 1-minute stem as WAV."""
    writer = ExportWriter(ExportConfig(format=ExportFormat.WAV))

    def _write() -> None:
        _run(
            writer.write_stem(
                "vocals", synthetic_stems["vocals"], _stem_path(tmp_export_dir, "wav")
            )
        )

    benchmark(_write)


def test_bench_export_flac_1min(
    benchmark, tmp_export_dir: Path, synthetic_stems: dict[str, np.ndarray]
) -> None:
    """Export one 1-minute stem as FLAC."""
    writer = ExportWriter(ExportConfig(format=ExportFormat.FLAC))

    def _write() -> None:
        _run(
            writer.write_stem(
                "vocals", synthetic_stems["vocals"], _stem_path(tmp_export_dir, "flac")
            )
        )

    benchmark(_write)


def test_bench_export_mp3_1min(
    benchmark, tmp_export_dir: Path, synthetic_stems: dict[str, np.ndarray]
) -> None:
    """Export one 1-minute stem as MP3."""
    writer = ExportWriter(ExportConfig(format=ExportFormat.MP3))

    def _write() -> None:
        _run(
            writer.write_stem(
                "vocals", synthetic_stems["vocals"], _stem_path(tmp_export_dir, "mp3")
            )
        )

    benchmark(_write)


def test_bench_export_m4a_1min(
    benchmark, tmp_export_dir: Path, synthetic_stems: dict[str, np.ndarray]
) -> None:
    """Export one 1-minute stem as M4A."""
    writer = ExportWriter(ExportConfig(format=ExportFormat.M4A))

    def _write() -> None:
        _run(
            writer.write_stem(
                "vocals", synthetic_stems["vocals"], _stem_path(tmp_export_dir, "m4a")
            )
        )

    benchmark(_write)


def test_bench_export_batch_sequential(
    benchmark, tmp_export_dir: Path, synthetic_stems: dict[str, np.ndarray]
) -> None:
    """Batch-export all stems sequentially."""
    exporter = BatchExporter(ExportConfig(format=ExportFormat.WAV))

    def _batch() -> None:
        _run(exporter.export_all(synthetic_stems, tmp_export_dir))

    benchmark(_batch)


def test_bench_export_batch_parallel(
    benchmark, tmp_export_dir: Path, synthetic_stems: dict[str, np.ndarray]
) -> None:
    """Batch-export all stems in parallel."""
    exporter = BatchExporter(ExportConfig(format=ExportFormat.WAV))

    def _batch() -> None:
        _run(exporter.export_parallel(synthetic_stems, tmp_export_dir))

    benchmark(_batch)
