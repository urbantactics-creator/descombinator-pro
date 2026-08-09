"""Offscreen validation for the settings / export-wiring fixes.

Covers the three scenarios from the plan's Validation section:
  1. save_settings emits no enum serialization warning;
  2. SettingsDialog export controls round-trip through save/reload;
  3. a built ExportConfig drives a real ExportService write (format honored).
"""

import asyncio
import warnings
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import soundfile as sf

from app.controllers.main_controller import MainController
from app.controllers.settings_controller import SettingsController
from app.models.settings_model import SettingsModel
from app.services.export_service import ExportService
from app.ui.settings_dialog import SettingsDialog
from engine.export.config import ExportFormat


def _real_controller(tmp_path: Path) -> SettingsController:
    controller = SettingsController()
    controller._settings_file = tmp_path / "settings.json"
    return controller


def test_save_settings_no_enum_warning(tmp_path) -> None:
    """Scenario 1: persisting settings must not warn about enum serialization."""
    controller = _real_controller(tmp_path)
    # Plain-str enum values are the exact case that triggered the warning.
    controller._settings = SettingsModel(
        default_model="mdx_extra", default_format="mp3"
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert controller.save_settings(controller._settings) is True
    assert controller._settings_file.exists()


def test_dialog_export_roundtrip(qapp, tmp_path) -> None:
    """Scenario 2: change every export control, save, reload, assert round-trip."""
    controller = _real_controller(tmp_path)

    dialog = SettingsDialog(controller)
    try:
        dialog._sample_rate_spin.setValue(48000)
        dialog._bit_depth_combo.setCurrentText("24")
        dialog._bitrate_spin.setValue(256)
        dialog._normalize_check.setChecked(False)
        dialog._fade_in_spin.setValue(1500)
        dialog._fade_out_spin.setValue(500)
        dialog._on_save()
    finally:
        dialog.close()
        dialog.deleteLater()

    # Reload from the persisted file via a fresh controller + dialog.
    reloaded = _real_controller(tmp_path)
    reloaded.load_settings()
    assert reloaded.settings.sample_rate == 48000
    assert reloaded.settings.bit_depth == 24
    assert reloaded.settings.bitrate == 256000
    assert reloaded.settings.normalize is False
    assert reloaded.settings.fade_in == 1.5
    assert reloaded.settings.fade_out == 0.5

    dialog2 = SettingsDialog(reloaded)
    try:
        assert dialog2._sample_rate_spin.value() == 48000
        assert dialog2._bit_depth_combo.currentText() == "24"
        assert dialog2._bitrate_spin.value() == 256
        assert dialog2._normalize_check.isChecked() is False
        assert dialog2._fade_in_spin.value() == 1500
        assert dialog2._fade_out_spin.value() == 500
    finally:
        dialog2.close()
        dialog2.deleteLater()


def test_export_service_honors_built_config(tmp_path) -> None:
    """Scenario 3: a built ExportConfig drives a real ExportService write."""
    controller = MagicMock(spec=SettingsController)
    controller.settings = SettingsModel()
    controller.settings.default_format = "flac"
    controller.settings.sample_rate = 48000
    controller.settings.bitrate = 256000

    main = MainController(settings=controller.settings, export_service=ExportService())
    config = main._build_export_config()
    assert config.format == ExportFormat.FLAC
    # Mirror the real wiring in handle_export_requested.
    main._export_service.update_config(config)

    stems = {
        "vocals": (np.sin(2 * np.pi * 440 * np.linspace(0, 1, 48000)) * 0.5).astype(
            np.float32
        )
    }
    results = asyncio.run(main._export_service.export_stems(stems, tmp_path))
    out = results["vocals"]
    # The built config drives the writer: configured format is honored on disk.
    assert out.suffix == ".flac"
    assert out.exists()
    data, sr = sf.read(out)
    assert data.shape[0] > 0
    # NOTE: ExportWriter.write() uses its own sample_rate default rather than
    # config.sample_rate, so configured sample_rate is not yet applied to the
    # written file. That is an engine-writer concern outside this plan's scope
    # (see plan: "Don't touch engine/"). The wiring correctness is asserted via
    # the built config below.
    assert config.sample_rate == 48000
    assert config.bitrate == 256000
