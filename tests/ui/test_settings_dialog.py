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


def test_settings_dialog_creation(qapp):
    """Test that SettingsDialog can be created."""
    dialog, _ = _make_dialog(qapp)
    assert dialog is not None
    assert dialog.windowTitle() == "Settings"


def test_settings_dialog_loads_values(qapp):
    """Test that current settings are loaded into the controls."""
    dialog, _ = _make_dialog(qapp)
    assert dialog._model_combo.currentData() == ModelName.HTDEMUCS_FT
    assert dialog._format_combo.currentData() == ExportFormat.WAV
    assert dialog._theme_combo.currentText() == "dark"
    assert dialog._output_dir_label.text() == "/tmp/out"
    assert dialog._segment_spin.value() == 0


def test_settings_dialog_change_model(qapp):
    """Test changing the model combo updates the selection."""
    dialog, _ = _make_dialog(qapp)
    idx = dialog._model_combo.findData(ModelName.MDX_EXTRA)
    dialog._model_combo.setCurrentIndex(idx)
    assert dialog._model_combo.currentData() == ModelName.MDX_EXTRA


def test_settings_dialog_change_format(qapp):
    """Test changing the format combo updates the selection."""
    dialog, _ = _make_dialog(qapp)
    idx = dialog._format_combo.findData(ExportFormat.FLAC)
    dialog._format_combo.setCurrentIndex(idx)
    assert dialog._format_combo.currentData() == ExportFormat.FLAC


def test_settings_dialog_save(qapp):
    """Test saving persists the settings through the controller."""
    dialog, controller = _make_dialog(qapp)
    dialog._theme_combo.setCurrentText("light")
    dialog._segment_spin.setValue(60)
    dialog._on_save()
    controller.save_settings.assert_called_once()
    controller.settings_changed.emit.assert_called_once()


def test_settings_dialog_browse_output_dir(qapp):
    """Test browsing sets the output directory label."""
    dialog, _ = _make_dialog(qapp)
    with patch(
        "app.ui.settings_dialog.QFileDialog.getExistingDirectory",
        return_value="/chosen/dir",
    ):
        dialog._browse_output_dir()
    assert dialog._output_dir_label.text() == "/chosen/dir"


def test_settings_dialog_save_error(qapp):
    """Test that a save failure shows a warning and does not close."""
    dialog, controller = _make_dialog(qapp)
    controller.save_settings.side_effect = RuntimeError("boom")
    with patch("app.ui.settings_dialog.QMessageBox.warning") as mock_warning:
        dialog._on_save()
    mock_warning.assert_called_once()
