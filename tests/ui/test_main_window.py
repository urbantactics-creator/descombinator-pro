"""Behavioral tests for MainWindow."""

from pathlib import Path
from unittest.mock import MagicMock

import numpy as np

from app.controllers.main_controller import MainController
from app.controllers.playback_controller import PlaybackController
from app.controllers.settings_controller import SettingsController
from app.models.app_state import AppState
from app.models.processing_state import ProcessingState
from app.models.settings_model import SettingsModel
from app.ui.main_window import MainWindow


def test_main_window_creation(qapp):
    """Test that MainWindow can be created."""
    main_controller = MagicMock(spec=MainController)
    playback_controller = MagicMock(spec=PlaybackController)
    settings_controller = MagicMock(spec=SettingsController)
    settings_controller.settings = SettingsModel()

    window = MainWindow(main_controller, playback_controller, settings_controller)
    assert window is not None
    assert window.windowTitle() == "Descombinator Pro"


def test_main_window_separate_button_disabled_initially(qapp):
    """Test that separate button is disabled initially."""
    main_controller = MagicMock(spec=MainController)
    main_controller._app_state = AppState()
    playback_controller = MagicMock(spec=PlaybackController)
    settings_controller = MagicMock(spec=SettingsController)
    settings_controller.settings = SettingsModel()

    window = MainWindow(main_controller, playback_controller, settings_controller)
    assert not window._separate_btn.isEnabled()


def test_main_window_separate_button_enabled_after_file_drop(qapp):
    """Test that separate button enables after file drop."""
    main_controller = MagicMock(spec=MainController)
    main_controller._app_state = AppState()
    playback_controller = MagicMock(spec=PlaybackController)
    settings_controller = MagicMock(spec=SettingsController)
    settings_controller.settings = SettingsModel()

    window = MainWindow(main_controller, playback_controller, settings_controller)
    window._on_file_dropped("/tmp/test.wav")
    assert window._separate_btn.isEnabled()


def test_main_window_state_changed_disables_ui_during_processing(qapp):
    """Test that UI disables during processing state."""
    main_controller = MagicMock(spec=MainController)
    main_controller._app_state = AppState()
    playback_controller = MagicMock(spec=PlaybackController)
    settings_controller = MagicMock(spec=SettingsController)
    settings_controller.settings = SettingsModel()

    window = MainWindow(main_controller, playback_controller, settings_controller)
    window._on_file_dropped("/tmp/test.wav")
    assert window._separate_btn.isEnabled()

    # Simulate LOADING state. Set the controller's current file so the
    # re-enable logic in _on_state_changed can evaluate correctly.
    main_controller._app_state.current_file = Path("/tmp/test.wav")
    app_state = AppState()
    app_state.current_file = Path("/tmp/test.wav")
    app_state.processing_status = ProcessingState.LOADING
    window._on_state_changed(app_state)
    assert not window._separate_btn.isEnabled()
    assert not window._file_drop_zone.isEnabled()
    assert not window._track_selector.isEnabled()

    # Simulate PROCESSING state
    app_state.processing_status = ProcessingState.PROCESSING
    window._on_state_changed(app_state)
    assert not window._separate_btn.isEnabled()

    # Simulate COMPLETE state
    app_state.processing_status = ProcessingState.COMPLETE
    window._on_state_changed(app_state)
    assert window._separate_btn.isEnabled()


def test_main_window_export_action_enabled_after_separation(qapp):
    """Test that export action enables after separation completes."""
    main_controller = MagicMock(spec=MainController)
    main_controller._app_state = AppState()
    playback_controller = MagicMock(spec=PlaybackController)
    settings_controller = MagicMock(spec=SettingsController)
    settings_controller.settings = SettingsModel()

    window = MainWindow(main_controller, playback_controller, settings_controller)
    assert not window._export_action.isEnabled()

    # Simulate separation completed
    stems = {"vocals": np.zeros(44100), "drums": np.zeros(44100)}
    main_controller._loaded_sample_rate = 44100
    window._on_separation_completed(stems)
    assert window._export_action.isEnabled()


def test_main_window_theme_change(qapp):
    """Test that theme change applies stylesheet."""
    main_controller = MagicMock(spec=MainController)
    main_controller._app_state = AppState()
    playback_controller = MagicMock(spec=PlaybackController)
    settings_controller = MagicMock(spec=SettingsController)
    settings_controller.settings = SettingsModel()

    window = MainWindow(main_controller, playback_controller, settings_controller)
    # Should not raise
    window._change_theme("dark")
    window._change_theme("light")


def test_main_window_close_event_cancels_worker(qapp):
    """Test that close event cancels running worker."""
    main_controller = MagicMock(spec=MainController)
    main_controller._app_state = AppState()
    main_controller._current_worker = MagicMock()
    playback_controller = MagicMock(spec=PlaybackController)
    settings_controller = MagicMock(spec=SettingsController)
    settings_controller.settings = SettingsModel()

    window = MainWindow(main_controller, playback_controller, settings_controller)
    from PySide6.QtGui import QCloseEvent

    event = QCloseEvent()
    window.closeEvent(event)
    main_controller.cancel_separation.assert_called_once()
    playback_controller.stop.assert_called_once()
    assert event.isAccepted()


def test_main_window_separation_completed_updates_waveform(qapp):
    """Test that separation completed updates waveform with correct sample rate."""
    main_controller = MagicMock(spec=MainController)
    main_controller._app_state = AppState()
    main_controller._loaded_sample_rate = 48000
    playback_controller = MagicMock(spec=PlaybackController)
    settings_controller = MagicMock(spec=SettingsController)
    settings_controller.settings = SettingsModel()

    window = MainWindow(main_controller, playback_controller, settings_controller)
    stems = {"vocals": np.zeros(48000), "drums": np.zeros(48000)}
    window._on_separation_completed(stems)
    # Verify waveform view received the correct sample rate
    assert window._waveform_view._audio_data is not None
    # The sample rate used should be 48000 (from _loaded_sample_rate)
    # We can't easily test the internal call, but we can verify no crash
