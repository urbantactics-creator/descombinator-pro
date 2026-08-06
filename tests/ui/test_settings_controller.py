"""UI integration tests exercising the real SettingsController."""

import json
from pathlib import Path

from app.controllers.settings_controller import SettingsController
from app.models.settings_model import SettingsModel
from engine.export.config import ExportFormat
from engine.inference.config import ModelName


def _controller_with_file(path: Path) -> SettingsController:
    controller = SettingsController()
    controller._settings_file = path
    return controller


def test_settings_controller_defaults(qapp):
    """Test the controller starts with default settings."""
    controller = SettingsController()
    assert controller._settings.theme == "dark"
    assert controller._settings.default_model == ModelName.HTDEMUCS_FT


def test_settings_controller_save_roundtrip(qapp, tmp_path):
    """Test settings are saved and reloaded."""
    settings_file = tmp_path / "settings.json"
    controller = _controller_with_file(settings_file)
    saved = controller.save_settings(
        SettingsModel(theme="light", segment=60, default_format=ExportFormat.FLAC)
    )
    assert saved is True

    controller2 = _controller_with_file(settings_file)
    loaded = controller2.load_settings()
    assert loaded.theme == "light"
    assert loaded.segment == 60
    assert loaded.default_format == ExportFormat.FLAC


def test_settings_controller_load_missing_file(qapp, tmp_path):
    """Test loading defaults when no settings file exists."""
    controller = _controller_with_file(tmp_path / "nonexistent.json")
    loaded = controller.load_settings()
    assert loaded.theme == "dark"


def test_settings_controller_load_corrupt_file(qapp, tmp_path):
    """Test loading falls back to defaults on corrupt JSON."""
    settings_file = tmp_path / "settings.json"
    settings_file.write_text("{not valid json")
    controller = _controller_with_file(settings_file)
    loaded = controller.load_settings()
    assert loaded.theme == "dark"


def test_settings_controller_update_setting(qapp, tmp_path):
    """Test update_setting persists a single setting."""
    controller = _controller_with_file(tmp_path / "settings.json")
    result = controller.update_setting("theme", "light")
    assert result is True
    assert controller._settings.theme == "light"


def test_settings_controller_update_unknown_key(qapp, tmp_path):
    """Test update_setting rejects unknown keys."""
    controller = _controller_with_file(tmp_path / "settings.json")
    result = controller.update_setting("not_a_key", 1)
    assert result is False


def test_settings_controller_reset(qapp, tmp_path):
    """Test reset_to_defaults restores default settings."""
    controller = _controller_with_file(tmp_path / "settings.json")
    controller._settings.theme = "light"
    defaults = controller.reset_to_defaults()
    assert defaults.theme == "dark"


def test_settings_controller_saved_file_content(qapp, tmp_path):
    """Test the saved JSON file contains the settings."""
    settings_file = tmp_path / "settings.json"
    controller = _controller_with_file(settings_file)
    controller.save_settings(SettingsModel(theme="light"))
    data = json.loads(settings_file.read_text())
    assert data["theme"] == "light"
    assert isinstance(data["output_dir"], str)
