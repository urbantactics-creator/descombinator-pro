"""Tests for building ExportConfig from persisted settings in MainController."""

from unittest.mock import MagicMock

import pytest

from app.controllers.main_controller import MainController
from app.models.settings_model import SettingsModel
from app.services.export_service import ExportService
from engine.export.config import ExportConfig, ExportFormat


class TestBuildExportConfigFromSettings:
    """Verify _build_export_config reflects persisted settings."""

    @pytest.fixture
    def main_controller(self):
        export_service = MagicMock(spec=ExportService)
        return MainController(
            settings=SettingsModel(),
            export_service=export_service,
        )

    def test_defaults(self, main_controller) -> None:
        config = main_controller._build_export_config()
        assert isinstance(config, ExportConfig)
        assert config.format == ExportFormat.WAV
        assert config.sample_rate == 44100
        assert config.bit_depth == 16
        assert config.bitrate == 192000
        assert config.normalize is True
        assert config.fade_in == 0.0
        assert config.fade_out == 0.0

    def test_custom_settings(self, main_controller) -> None:
        s = main_controller._app_state.settings
        s.default_format = "mp3"
        s.sample_rate = 48000
        s.bit_depth = 24
        s.bitrate = 256000
        s.normalize = False
        s.fade_in = 1.5
        s.fade_out = 0.5

        config = main_controller._build_export_config()
        assert config.format == ExportFormat.MP3
        assert config.sample_rate == 48000
        assert config.bit_depth == 24
        assert config.bitrate == 256000
        assert config.normalize is False
        assert config.fade_in == 1.5
        assert config.fade_out == 0.5

    def test_handle_export_requested_applies_config(self, main_controller) -> None:
        s = main_controller._app_state.settings
        s.bitrate = 256000
        s.sample_rate = 48000

        main_controller.handle_export_requested(
            output_dir="/tmp/out", stems={"vocals": MagicMock()}
        )

        main_controller._export_service.update_config.assert_called_once()
        applied = main_controller._export_service.update_config.call_args[0][0]
        assert isinstance(applied, ExportConfig)
        assert applied.bitrate == 256000
        assert applied.sample_rate == 48000

    def test_on_settings_changed_rebuilds_separation_config(
        self, main_controller
    ) -> None:
        from engine.demucs.config import ModelName, SeparationConfig

        new_settings = SettingsModel(default_model="mdx_extra", segment=12)
        main_controller.on_settings_changed(new_settings)

        assert main_controller._app_state.settings is new_settings
        config = main_controller._build_separation_config()
        assert isinstance(config, SeparationConfig)
        assert config.model_name == ModelName.MDX_EXTRA
        assert config.segment == 12

    def test_on_settings_changed_skips_rebuild_while_busy(
        self, main_controller
    ) -> None:
        from unittest.mock import MagicMock

        main_controller._current_worker = MagicMock()
        original_service = main_controller._separation_service
        new_settings = SettingsModel(default_model="mdx_extra")

        main_controller.on_settings_changed(new_settings)

        assert main_controller._app_state.settings is new_settings
        assert main_controller._separation_service is original_service
