"""Behavioral tests for the SettingsDialog."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from app.controllers.settings_controller import SettingsController
from app.ui.settings_dialog import SettingsDialog
from engine.export.config import ExportFormat
from engine.inference.config import ModelName


def _make_dialog(qapp):
    controller = MagicMock(spec=SettingsController)
    controller._settings = MagicMock()
    controller._settings.model_dump.return_value = {
        "output_dir": Path("/tmp/out"),
        "default_model": ModelName.HTDEMUCS_FT,
        "default_format": ExportFormat.WAV,
        "theme": "dark",
        "segment": None,
        "mixed_precision": False,
        "pin_memory": False,
    }
    controller.settings_changed = MagicMock()
    dialog = SettingsDialog(controller)
    return dialog, controller


def _cleanup(dialog):
    dialog.close()
    dialog.deleteLater()


def test_settings_dialog_creation(qapp):
    """Test that SettingsDialog can be created."""
    dialog, _ = _make_dialog(qapp)
    try:
        assert dialog is not None
        assert dialog.windowTitle() == "Settings"
    finally:
        _cleanup(dialog)


def test_settings_dialog_loads_values(qapp):
    """Test that current settings are loaded into the controls."""
    dialog, _ = _make_dialog(qapp)
    try:
        assert dialog._model_combo.currentData() == ModelName.HTDEMUCS_FT
        assert dialog._format_combo.currentData() == ExportFormat.WAV
        assert dialog._theme_combo.currentText() == "dark"
        assert dialog._output_dir_label.text() == "/tmp/out"
        assert dialog._segment_spin.value() == 0
    finally:
        _cleanup(dialog)


def test_settings_dialog_change_model(qapp):
    """Test changing the model combo updates the selection."""
    dialog, _ = _make_dialog(qapp)
    try:
        idx = dialog._model_combo.findData(ModelName.MDX_EXTRA)
        dialog._model_combo.setCurrentIndex(idx)
        assert dialog._model_combo.currentData() == ModelName.MDX_EXTRA
    finally:
        _cleanup(dialog)


def test_settings_dialog_change_format(qapp):
    """Test changing the format combo updates the selection."""
    dialog, _ = _make_dialog(qapp)
    try:
        idx = dialog._format_combo.findData(ExportFormat.FLAC)
        dialog._format_combo.setCurrentIndex(idx)
        assert dialog._format_combo.currentData() == ExportFormat.FLAC
    finally:
        _cleanup(dialog)


def test_settings_dialog_save(qapp):
    """Test saving persists the settings through the controller."""
    dialog, controller = _make_dialog(qapp)
    try:
        dialog._theme_combo.setCurrentText("light")
        dialog._segment_spin.setValue(60)
        dialog._on_save()
        controller.save_settings.assert_called_once()
        controller.settings_changed.emit.assert_called_once()
    finally:
        _cleanup(dialog)


def test_settings_dialog_browse_output_dir(qapp):
    """Test browsing sets the output directory label."""
    dialog, _ = _make_dialog(qapp)
    try:
        with patch(
            "app.ui.settings_dialog.QFileDialog.getExistingDirectory",
            return_value="/chosen/dir",
        ):
            dialog._browse_output_dir()
        assert dialog._output_dir_label.text() == "/chosen/dir"
    finally:
        _cleanup(dialog)


def test_settings_dialog_save_error(qapp):
    """Test that a save failure shows a warning and does not close."""
    dialog, controller = _make_dialog(qapp)
    try:
        controller.save_settings.side_effect = RuntimeError("boom")
        with patch("app.ui.settings_dialog.QMessageBox.warning") as mock_warning:
            dialog._on_save()
        mock_warning.assert_called_once()
    finally:
        _cleanup(dialog)


def test_settings_dialog_export_roundtrip(qapp):
    """Test that export controls load and save with kbps<->bps conversion."""
    dialog, controller = _make_dialog(qapp)
    try:
        # Change every export control
        dialog._sample_rate_spin.setValue(48000)
        dialog._bit_depth_combo.setCurrentText("24")
        dialog._bitrate_spin.setValue(256)  # kbps
        dialog._normalize_check.setChecked(False)
        dialog._fade_in_spin.setValue(1500)  # ms
        dialog._fade_out_spin.setValue(500)  # ms
        dialog._on_save()

        saved = controller._settings
        assert saved.sample_rate == 48000
        assert saved.bit_depth == 24
        assert saved.bitrate == 256000  # kbps -> bps
        assert saved.normalize is False
        assert saved.fade_in == 1.5  # ms -> s
        assert saved.fade_out == 0.5  # ms -> s
    finally:
        _cleanup(dialog)


def test_settings_dialog_loads_export_values(qapp):
    """Test that persisted export values are loaded into the controls."""
    controller = MagicMock(spec=SettingsController)
    controller._settings = MagicMock()
    controller._settings.model_dump.return_value = {
        "output_dir": Path("/tmp/out"),
        "default_model": ModelName.HTDEMUCS_FT,
        "default_format": ExportFormat.WAV,
        "theme": "dark",
        "segment": None,
        "mixed_precision": False,
        "pin_memory": False,
        "sample_rate": 48000,
        "bit_depth": 24,
        "bitrate": 256000,
        "normalize": False,
        "fade_in": 1.5,
        "fade_out": 0.5,
    }
    controller.settings_changed = MagicMock()
    dialog = SettingsDialog(controller)
    try:
        assert dialog._sample_rate_spin.value() == 48000
        assert dialog._bit_depth_combo.currentText() == "24"
        assert dialog._bitrate_spin.value() == 256  # bps -> kbps
        assert dialog._normalize_check.isChecked() is False
        assert dialog._fade_in_spin.value() == 1500  # s -> ms
        assert dialog._fade_out_spin.value() == 500  # s -> ms
    finally:
        _cleanup(dialog)
