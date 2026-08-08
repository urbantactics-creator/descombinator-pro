"""Controller for managing application settings."""

import json
from pathlib import Path

from loguru import logger
from PySide6.QtCore import QObject, Signal

from app.models.settings_model import SettingsModel


class SettingsController(QObject):
    """Controller for managing application settings."""

    settings_changed = Signal(object)  # SettingsModel
    settings_saved = Signal(bool)  # Success flag
    settings_loaded = Signal(bool)  # Success flag

    def __init__(self) -> None:
        """Initialize the settings controller and create the settings directory."""
        super().__init__()
        self._settings_file = Path.home() / ".descombinator" / "settings.json"
        self._settings_file.parent.mkdir(parents=True, exist_ok=True)
        self._settings: SettingsModel = SettingsModel()

    @property
    def settings(self) -> SettingsModel:
        """Current settings model."""
        return self._settings

    def load_settings(self) -> SettingsModel:
        """Load settings from file.

        Returns:
            SettingsModel: Loaded settings or default settings if file doesn't exist
        """
        try:
            if self._settings_file.exists():
                with open(self._settings_file) as f:
                    data = json.load(f)
                self._settings = SettingsModel(**data)
                logger.info(f"Loaded settings from {self._settings_file}")
            else:
                self._settings = SettingsModel()
                logger.info("Using default settings")
        except Exception as e:
            logger.warning(f"Failed to load settings: {e}")
            self._settings = SettingsModel()

        self.settings_loaded.emit(True)
        return self._settings

    def save_settings(self, settings: SettingsModel) -> bool:
        """Save settings to file.

        Args:
            settings: Settings to save

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert to dict, handling Path objects
            data = settings.model_dump()
            # Convert Path to string for JSON serialization
            if isinstance(data.get("output_dir"), Path):
                data["output_dir"] = str(data["output_dir"])

            with open(self._settings_file, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved settings to {self._settings_file}")
            self.settings_saved.emit(True)
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            self.settings_saved.emit(False)
            return False

    def update_setting(self, key: str, value: object) -> bool:
        """Update a single setting.

        Args:
            key: Setting name
            value: Setting value

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if key not in SettingsModel.model_fields:
                logger.warning(f"Unknown setting: {key}")
                return False
            setattr(self._settings, key, value)
            return self.save_settings(self._settings)
        except Exception as e:
            logger.error(f"Failed to update setting {key}: {e}")
            return False

    def reset_to_defaults(self) -> SettingsModel:
        """Reset settings to default values.

        Returns:
            SettingsModel: Default settings
        """
        default_settings = SettingsModel()
        self.save_settings(default_settings)
        return default_settings
