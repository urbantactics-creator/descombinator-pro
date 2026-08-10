"""Slow integration test for ExportWorker with a real QApplication.

This test exercises the actual export path that was previously blocking the
UI thread. It is marked ``slow`` so it is excluded from the default CI run,
but can be executed manually or in a nightly job.
"""

from pathlib import Path

import numpy as np
import pytest

from app.controllers.main_controller import ExportWorker
from app.services.export_service import ExportService
from engine.export.config import ExportConfig, ExportFormat


@pytest.fixture
def export_service(tmp_path: Path) -> ExportService:
    """Return an ExportService configured for WAV output in a temp directory."""
    return ExportService(ExportConfig(format=ExportFormat.WAV))


@pytest.fixture
def sample_stems() -> dict[str, np.ndarray]:
    """Generate tiny synthetic stems for fast export."""
    sr = 44100
    t = np.linspace(0, 0.1, int(sr * 0.1), endpoint=False)
    return {
        "vocals": (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32),
        "drums": (np.sin(2 * np.pi * 880 * t) * 0.3).astype(np.float32),
    }


class TestExportWorkerIntegration:
    """Integration tests for ExportWorker running off the UI thread."""

    @pytest.mark.slow
    def test_export_worker_finishes_without_blocking_ui(
        self,
        qtbot,
        export_service: ExportService,
        sample_stems: dict[str, np.ndarray],
        tmp_path: Path,
    ) -> None:
        """ExportWorker emits finished without blocking the UI event loop."""
        finished_results: dict[str, Path] | None = None
        error_result: Exception | None = None

        def on_finished(result: dict[str, Path]) -> None:
            nonlocal finished_results
            finished_results = result

        def on_error(exc: Exception) -> None:
            nonlocal error_result
            error_result = exc

        worker = ExportWorker(
            export_service,
            sample_stems,
            tmp_path,
        )
        worker.signals.finished.connect(on_finished)
        worker.signals.error.connect(on_error)

        # Start the worker and verify the UI remains responsive by waiting
        # for the finished signal with a reasonable timeout.
        with qtbot.waitSignal(worker.signals.finished, timeout=30000):
            worker.run()

        assert error_result is None, f"Export failed: {error_result}"
        assert finished_results is not None
        for stem_name, path in finished_results.items():
            assert path.exists()
            assert path.suffix == ".wav"
            assert stem_name in sample_stems
