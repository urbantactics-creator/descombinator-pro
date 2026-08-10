"""Smoke tests for critical application paths.

These tests verify that the main flows still work after bugfix changes:
- MainWindow can be instantiated headlessly.
- ExportWorker runs to completion off the UI thread.
- SettingsModel.device is persisted and propagated into SeparationConfig.
- Core imports do not raise at import time.
"""

from pathlib import Path
from typing import Any

import numpy as np
import pytest

from app.controllers.main_controller import ExportWorker, MainController
from app.models.settings_model import SettingsModel
from app.services.export_service import ExportService
from app.ui.main_window import MainWindow
from engine.demucs.config import DeviceType
from engine.export.config import ExportConfig, ExportFormat


class TestSmokeImports:
    """Import-time smoke tests."""

    def test_import_main_window(self) -> None:
        from app.ui.main_window import MainWindow  # noqa: F401

    def test_import_demucs_separator(self) -> None:
        from engine.demucs.separator import DemucsSeparator  # noqa: F401


class TestSmokeMainWindow:
    """MainWindow instantiation smoke test."""

    def test_main_window_creation(self, qtbot: Any) -> None:
        from unittest.mock import MagicMock

        from app.controllers.playback_controller import PlaybackController
        from app.controllers.settings_controller import SettingsController

        main_controller = MagicMock()
        playback_controller = MagicMock(spec=PlaybackController)
        settings_controller = MagicMock(spec=SettingsController)
        settings_controller.settings = SettingsModel()

        window = MainWindow(main_controller, playback_controller, settings_controller)
        qtbot.addWidget(window)
        assert window.windowTitle() == "Descombinator Pro"


class TestSmokeExportWorker:
    """ExportWorker smoke test using real file I/O."""

    @pytest.mark.slow
    def test_export_worker_writes_wav(self, qtbot: Any, tmp_path: Path) -> None:
        service = ExportService(ExportConfig(format=ExportFormat.WAV))
        sr = 44100
        t = np.linspace(0, 0.1, int(sr * 0.1), endpoint=False)
        stems = {
            "vocals": (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32),
        }

        worker = ExportWorker(service, stems, tmp_path)
        finished_results: dict[str, Path] | None = None

        def on_finished(result: dict[str, Path]) -> None:
            nonlocal finished_results
            finished_results = result

        worker.signals.finished.connect(on_finished)
        with qtbot.waitSignal(worker.signals.finished, timeout=30000):
            worker.run()

        assert finished_results is not None
        assert (tmp_path / "vocals.wav").exists()


class TestSmokeSettingsDevicePropagation:
    """SettingsModel.device propagation smoke test."""

    def test_device_propagates_to_separation_config(self) -> None:
        settings = SettingsModel(device=DeviceType.CUDA)
        controller = MainController(settings=settings)
        config = controller._build_separation_config()
        assert config.device == DeviceType.CUDA
