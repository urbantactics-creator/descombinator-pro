"""Tests for the controllers."""

from app.controllers.main_controller import MainController
from app.controllers.playback_controller import PlaybackController
from app.controllers.settings_controller import SettingsController


def test_controllers_creation(qapp):
    """Test that controllers can be created."""
    main_controller = MainController()
    assert main_controller is not None

    playback_controller = PlaybackController()
    assert playback_controller is not None

    settings_controller = SettingsController()
    assert settings_controller is not None
