"""Comprehensive tests for SettingsController."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.controllers.settings_controller import SettingsController
from app.models.settings_model import SettingsModel
from engine.export.config import ExportConfig, ExportFormat
from engine.inference.config import InferenceConfig, DeviceType
from engine.inference.config import ModelName


class TestSettingsController:
    """Comprehensive tests for SettingsController."""

    @pytest.fixture
    def settings_controller(self):
        """Create SettingsController."""
        return SettingsController()

    def test_initialization(self, settings_controller):
        """Test that SettingsController initializes correctly."""
        assert isinstance(settings_controller.settings, SettingsModel)
        # Note: The default output_dir may vary based on system configuration
        assert settings_controller.settings.default_model == ModelName.HTDEMUCS_FT
        assert settings_controller.settings.default_format == ExportFormat.WAV

    def test_get_settings(self, settings_controller):
        """Test getting settings."""
        settings = settings_controller.settings
        assert isinstance(settings, SettingsModel)
        assert settings is settings_controller.settings

    def test_update_setting(self, settings_controller):
        """Test updating a single setting."""
        result = settings_controller.update_setting("theme", "light")
        assert result is True
        assert settings_controller.settings.theme == "light"

        # Test updating another setting
        result = settings_controller.update_setting("segment", 5)
        assert result is True
        assert settings_controller.settings.segment == 5

    def test_update_setting_unknown_key(self, settings_controller):
        """Test updating an unknown setting key."""
        result = settings_controller.update_setting("unknown_key", "value")
        assert result is False  # Should return False for unknown keys
        # Settings should remain unchanged
        assert not hasattr(settings_controller.settings, "unknown_key")

    def test_update_setting_partial(self, settings_controller):
        """Test updating settings partially."""
        # Update multiple settings
        settings_controller.update_setting("theme", "light")
        settings_controller.update_setting("segment", 10)
        settings_controller.update_setting("reduced_motion", True)

        # Check that all settings were updated
        assert settings_controller.settings.theme == "light"
        assert settings_controller.settings.segment == 10
        assert settings_controller.settings.reduced_motion is True

        # Check that other settings remain unchanged
        assert settings_controller.settings.default_model == ModelName.HTDEMUCS_FT
        assert settings_controller.settings.default_format == ExportFormat.WAV
        assert settings_controller.settings.high_contrast is False

    def test_reset_to_defaults(self, settings_controller):
        """Test resetting settings to defaults."""
        # First modify some settings
        settings_controller.update_setting("output_dir", Path("/modified/output"))
        settings_controller.update_setting("default_model", ModelName.MDX_EXTRA)
        settings_controller.update_setting("theme", "test_theme")

        # Then reset to defaults
        default_settings = settings_controller.reset_to_defaults()

        # Check that values are back to defaults
        # Note: Default output directory is user-specific
        assert default_settings.default_model == ModelName.HTDEMUCS_FT
        assert default_settings.default_format == ExportFormat.WAV
        assert default_settings.theme == "dark"
        assert default_settings.reduced_motion is False
        assert default_settings.high_contrast is False
        assert default_settings.segment is None
        assert default_settings.mixed_precision is False
        assert default_settings.pin_memory is False

    def test_settings_model_validation(self, settings_controller):
        """Test that settings model validates correctly."""
        # Test valid settings
        settings = SettingsModel(
            output_dir=Path("/tmp/test"),
            default_model=ModelName.MDX_EXTRA,
            default_format=ExportFormat.MP3,
            theme="light",
            reduced_motion=True,
            high_contrast=False,
            segment=5,
            mixed_precision=True,
            pin_memory=True,
        )
        assert settings.output_dir == Path("/tmp/test")
        assert settings.default_model == ModelName.MDX_EXTRA
        assert settings.default_format == ExportFormat.MP3

    def test_export_config_creation(self, settings_controller):
        """Test creating ExportConfig from settings."""
        # This would typically be done in the controller when exporting
        settings = settings_controller.settings
        export_config = ExportConfig(
            format=settings.default_format,
            # Note: sample_rate, bitrate, bit_depth are ExportConfig defaults,
            # not stored in SettingsModel
        )
        assert export_config.format == settings.default_format
        # Check that defaults are applied
        assert export_config.sample_rate == 44100
        assert export_config.bitrate == 192000
        assert export_config.bit_depth == 16

    def test_inference_config_creation(self, settings_controller):
        """Test creating InferenceConfig from settings."""
        # This would typically be done in the controller when processing
        settings = settings_controller.settings
        inference_config = InferenceConfig(
            model_name=settings.default_model,
            # Other fields would come from settings or defaults
        )
        assert inference_config.model_name == settings.default_model
        # Check that defaults are applied
        assert inference_config.device == DeviceType.CPU
        assert inference_config.shifts == 1
        assert inference_config.overlap == 0.25
        assert inference_config.target_stems == ["vocals", "other"]