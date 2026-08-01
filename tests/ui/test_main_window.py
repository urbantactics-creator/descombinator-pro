"""Tests for the MainWindow."""

from app.controllers.main_controller import MainController
from app.controllers.playback_controller import PlaybackController
from app.controllers.settings_controller import SettingsController
from app.ui.main_window import MainWindow


def test_main_window_creation(qapp):
    """Test that MainWindow can be created."""
    # Create controllers
    main_controller = MainController()
    playback_controller = PlaybackController()
    settings_controller = SettingsController()

    # Create main window
    window = MainWindow(
        main_controller=main_controller,
        playback_controller=playback_controller,
        settings_controller=settings_controller,
    )

    assert window is not None
    assert window.windowTitle() == "Descombinator Pro"
    assert window.minimumWidth() == 800
    assert window.minimumHeight() == 600


def test_main_window_has_expected_widgets(qapp):
    """Test that MainWindow has the expected child widgets."""
    # Create controllers
    main_controller = MainController()
    playback_controller = PlaybackController()
    settings_controller = SettingsController()

    # Create main window
    window = MainWindow(
        main_controller=main_controller,
        playback_controller=playback_controller,
        settings_controller=settings_controller,
    )

    # Check for key widgets
    assert hasattr(window, "_file_drop_zone")
    assert hasattr(window, "_track_selector")
    assert hasattr(window, "_progress_bar")
    assert hasattr(window, "_waveform_view")
    assert hasattr(window, "_playback_controls")
    assert hasattr(window, "_status_label")
    assert hasattr(window, "_export_action")

    # Check that the export action is initially disabled
    assert not window._export_action.isEnabled()
