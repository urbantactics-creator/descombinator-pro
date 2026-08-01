"""Tests for the SettingsController."""

from __future__ import annotations

import json
from pathlib import Path

from app.controllers.settings_controller import SettingsController
from app.models.settings_model import SettingsModel


class TestSettingsControllerInit:
    """Tests for SettingsController initialization."""

    def test_creates_default_settings(self) -> None:
        """Controller creates with default settings."""
        ctrl = SettingsController()
        assert isinstance(ctrl._settings, SettingsModel)
        assert ctrl._settings.theme == "dark"

    def test_settings_file_path(self) -> None:
        """Settings file is in ~/.descombinator/settings.json."""
        ctrl = SettingsController()
        assert ctrl._settings_file == Path.home() / ".descombinator" / "settings.json"


class TestSettingsControllerLoad:
    """Tests for load_settings."""

    def test_load_default_when_no_file(self, tmp_path: Path) -> None:
        """Returns defaults when no settings file exists."""
        ctrl = SettingsController()
        ctrl._settings_file = tmp_path / "nonexistent.json"
        result = ctrl.load_settings()
        assert isinstance(result, SettingsModel)
        assert result.theme == "dark"

    def test_load_from_json_file(self, tmp_path: Path) -> None:
        """Loads settings from existing JSON file."""
        ctrl = SettingsController()
        settings_file = tmp_path / "settings.json"
        data = {"theme": "light", "output_dir": str(tmp_path / "output")}
        settings_file.write_text(json.dumps(data))

        ctrl._settings_file = settings_file
        result = ctrl.load_settings()

        assert result.theme == "light"
        assert ctrl._settings.theme == "light"

    def test_load_invalid_json_returns_defaults(self, tmp_path: Path) -> None:
        """Returns defaults when JSON is invalid."""
        ctrl = SettingsController()
        settings_file = tmp_path / "settings.json"
        settings_file.write_text("not valid json {{{")

        ctrl._settings_file = settings_file
        result = ctrl.load_settings()

        assert result.theme == "dark"
        assert ctrl._settings.theme == "dark"


class TestSettingsControllerSave:
    """Tests for save_settings."""

    def test_save_creates_file(self, tmp_path: Path) -> None:
        """Saving creates the settings file."""
        ctrl = SettingsController()
        ctrl._settings_file = tmp_path / "settings.json"

        settings = SettingsModel(theme="light")
        result = ctrl.save_settings(settings)

        assert result is True
        assert ctrl._settings_file.exists()

        with open(ctrl._settings_file) as f:
            data = json.load(f)
        assert data["theme"] == "light"

    def test_save_handles_path_serialization(self, tmp_path: Path) -> None:
        """Saving serializes Path objects to strings."""
        ctrl = SettingsController()
        ctrl._settings_file = tmp_path / "settings.json"

        settings = SettingsModel(output_dir=tmp_path / "music")
        ctrl.save_settings(settings)

        with open(ctrl._settings_file) as f:
            data = json.load(f)
        assert isinstance(data["output_dir"], str)


class TestSettingsControllerUpdate:
    """Tests for update_setting."""

    def test_update_existing_setting(self) -> None:
        """Updates an existing setting and persists it."""
        ctrl = SettingsController()
        ctrl._settings_file = Path("/dev/null")

        result = ctrl.update_setting("theme", "light")
        assert result is True
        assert ctrl._settings.theme == "light"

    def test_update_unknown_setting(self) -> None:
        """Returns False for unknown setting key."""
        ctrl = SettingsController()
        result = ctrl.update_setting("nonexistent_key", "value")
        assert result is False
