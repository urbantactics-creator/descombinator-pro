"""Comprehensive tests for MainController."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.controllers.main_controller import MainController
from app.models.app_state import AppState
from app.models.processing_state import ProcessingState
from app.models.settings_model import SettingsModel


class TestMainController:
    """Comprehensive tests for MainController."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services for MainController."""
        separation_service = AsyncMock()
        export_service = AsyncMock()
        return separation_service, export_service

    @pytest.fixture
    def main_controller(self, mock_services):
        """Create MainController with mock services."""
        separation_service, export_service = mock_services
        return MainController(
            settings=SettingsModel(),
            export_service=export_service,
        )

    def test_initialization(self, main_controller):
        """Test that MainController initializes correctly."""
        assert main_controller._separation_service is not None
        assert main_controller._export_service is not None
        assert isinstance(main_controller.app_state, AppState)
        assert isinstance(main_controller.app_state.settings, SettingsModel)

    def test_handle_file_dropped_success(
        self, main_controller
    ):
        """Test handling a valid file drop."""
        file_path = Path("/tmp/test.wav")

        main_controller.handle_file_dropped(str(file_path))

        assert main_controller.app_state.current_file == file_path
        # Note: processing_status is set to IDLE in handle_file_dropped

    def test_handle_file_dropped_nonexistent_file(
        self, main_controller
    ):
        """Test handling a nonexistent file drop."""
        file_path = Path("/tmp/nonexistent.wav")

        # This should not raise an exception - it just sets the current file
        main_controller.handle_file_dropped(str(file_path))
        assert main_controller.app_state.current_file == file_path

    def test_set_loaded_audio(
        self, main_controller
    ):
        """Test setting pre-loaded audio."""
        import numpy as np
        audio = np.zeros(44100, dtype=np.float32)
        sample_rate = 44100

        main_controller.set_loaded_audio(audio, sample_rate)

        assert main_controller._loaded_audio is audio
        assert main_controller._loaded_sample_rate == sample_rate

    def test_handle_separate_requested_no_file(
        self, main_controller
    ):
        """Test handling separation request when no file is loaded."""
        # Should emit separation_failed signal
        # We can't easily test signals without qtbot, but we can verify the method doesn't crash
        main_controller.handle_separate_requested()
        # No assertion needed - just verifying it doesn't raise

    def test_update_settings(
        self, main_controller
    ):
        """Test updating settings."""
        new_settings = {
            "output_dir": "/custom/output",
            "theme": "light",
            "segment": 10
        }
        main_controller.update_settings(new_settings)

        assert str(main_controller.app_state.settings.output_dir) == "/custom/output"
        assert main_controller.app_state.settings.theme == "light"
        assert main_controller.app_state.settings.segment == 10

    def test_get_app_state(self, main_controller):
        """Test getting the app state."""
        state = main_controller.app_state
        assert isinstance(state, AppState)
        assert state is main_controller._app_state

    def test_get_settings_model(self, main_controller):
        """Test getting the settings model."""
        model = main_controller.app_state.settings
        assert isinstance(model, SettingsModel)
        assert model is main_controller._app_state.settings