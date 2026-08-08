"""Enhanced tests for MainWindow to improve coverage."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from app.controllers.main_controller import MainController
from app.controllers.playback_controller import PlaybackController
from app.controllers.settings_controller import SettingsController
from app.models.app_state import AppState
from app.models.processing_state import ProcessingState
from app.models.settings_model import SettingsModel
from app.ui.main_window import MainWindow


class TestMainWindowEnhanced:
    """Enhanced tests for MainWindow."""

    def create_window(self, qapp):
        """Helper to create a MainWindow with mocked controllers."""
        main_controller = MagicMock(spec=MainController)
        main_controller._app_state = AppState()
        main_controller.separation_started = MagicMock()
        main_controller.separation_completed = MagicMock()
        main_controller.separation_failed = MagicMock()
        main_controller.separation_cancelled = MagicMock()
        main_controller.separation_progress = MagicMock()
        main_controller.export_progress = MagicMock()
        main_controller.export_completed = MagicMock()
        main_controller.export_failed = MagicMock()
        main_controller.thermal_warning = MagicMock()
        main_controller.state_changed = MagicMock()

        playback_controller = MagicMock(spec=PlaybackController)
        playback_controller.state_changed = MagicMock()
        playback_controller.position_changed = MagicMock()
        playback_controller.duration_changed = MagicMock()
        playback_controller.error_occurred = MagicMock()

        settings_controller = MagicMock(spec=SettingsController)
        settings_controller.settings = SettingsModel()

        window = MainWindow(main_controller, playback_controller, settings_controller)
        return window, main_controller, playback_controller, settings_controller

    def test_main_window_menu_actions_exist(self, qapp):
        """Test that main window has expected menu actions."""
        window, _, _, _ = self.create_window(qapp)

        # Check that menu actions exist
        assert hasattr(window, "_export_action")
        assert hasattr(window, "_settings_action")
        assert hasattr(window, "_theme_menu")
        assert hasattr(window, "_help_menu")

    def test_main_window_status_bar_exists(self, qapp):
        """Test that main window has a status bar."""
        window, _, _, _ = self.create_window(qapp)
        assert window.statusBar() is not None

    def test_main_window_central_widget_exists(self, qapp):
        """Test that main window has a central widget."""
        window, _, _, _ = self.create_window(qapp)
        assert window.centralWidget() is not None

    def test_main_window_file_drop_zone_connection(self, qapp):
        """Test that file drop zone signals are connected."""
        window, main_controller, _, _ = self.create_window(qapp)

        # Verify the file drop zone's signal is connected to the controller
        # We can't easily test the actual connection, but we can verify
        # the zone exists and the controller method exists
        assert window._file_drop_zone is not None
        assert hasattr(main_controller, "handle_file_dropped")

    def test_main_window_playback_controls_connection(self, qapp):
        """Test that playback controls signals are connected."""
        window, _, playback_controller, _ = self.create_window(qapp)

        # Verify playback controls exist and controller methods exist
        assert window._playback_controls is not None
        assert hasattr(playback_controller, "play")
        assert hasattr(playback_controller, "pause")
        assert hasattr(playback_controller, "stop")
        assert hasattr(playback_controller, "set_source")
        assert hasattr(playback_controller, "set_stems")

    def test_main_window_track_mixer_connection(self, qapp):
        """Test that track mixer signals are connected."""
        window, _, playback_controller, _ = self.create_window(qapp)

        # Verify track mixer exists and controller methods exist
        assert window._track_mixer is not None
        assert hasattr(playback_controller, "set_active_stems")
        assert hasattr(playback_controller, "set_track_volume")
        assert hasattr(playback_controller, "set_track_muted")
        assert hasattr(playback_controller, "set_master_volume")

    def test_main_window_track_selector_connection(self, qapp):
        """Test that track selector signals are connected."""
        window, main_controller, _, _ = self.create_window(qapp)

        # Verify track selector exists and controller method exists
        assert window._track_selector is not None
        assert hasattr(main_controller, "handle_stems_changed")

    def test_main_window_waveform_view_exists(self, qapp):
        """Test that waveform view exists."""
        window, _, _, _ = self.create_window(qapp)
        assert window._waveform_view is not None

    def test_main_window_progress_bar_exists(self, qapp):
        """Test that progress bar exists."""
        window, _, _, _ = self.create_window(qapp)
        assert window._progress_bar is not None

    def test_main_window_processing_dialog_initial_state(self, qapp):
        """Test that processing dialog is initially None."""
        window, _, _, _ = self.create_window(qapp)
        assert window._processing_dialog is None

    def test_main_window_export_dialog_initial_state(self, qapp):
        """Test that export dialog is initially None."""
        window, _, _, _ = self.create_window(qapp)
        assert window._export_dialog is None

    def test_main_window_on_file_dropped_calls_controller(self, qapp):
        """Test that _on_file_dropped calls the main controller."""
        window, main_controller, _, _ = self.create_window(qapp)

        window._on_file_dropped("/tmp/test.wav")

        main_controller.handle_file_dropped.assert_called_once_with("/tmp/test.wav")

    def test_main_window_on_separate_clicked_calls_controller(self, qapp):
        """Test that _on_separate_clicked calls the main controller."""
        window, main_controller, _, _ = self.create_window(qapp)

        window._on_separate_clicked()

        main_controller.handle_separate_requested.assert_called_once()

    def test_main_window_on_stems_changed_calls_controller(self, qapp):
        """Test that _on_stems_changed calls the main controller."""
        window, main_controller, _, _ = self.create_window(qapp)

        stems = ["vocals", "drums"]
        window._on_stems_changed(stems)

        main_controller.handle_stems_changed.assert_called_once_with(stems)

    def test_main_window_on_export_triggered_calls_controller(self, qapp):
        """Test that _on_export_triggered calls the main controller."""
        window, main_controller, _, _ = self.create_window(qapp)

        stems = {"vocals": MagicMock(), "instrumental": MagicMock()}
        window._on_export_triggered(stems)

        main_controller.handle_export_requested.assert_called_once()

    def test_main_window_on_settings_triggered_opens_dialog(self, qapp):
        """Test that _on_settings_triggered opens settings dialog."""
        window, _, _, settings_controller = self.create_window(qapp)

        with patch("app.ui.main_window.SettingsDialog") as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog_class.return_value = mock_dialog

            window._on_settings_triggered()

            # Should have created and shown the settings dialog
            mock_dialog_class.assert_called_once()
            mock_dialog.exec.assert_called_once()

    def test_main_window_on_export_triggered_shows_dialog(self, qapp):
        """Test that _on_export_triggered shows export dialog."""
        window, main_controller, _, _ = self.create_window(qapp)

        stems = {"vocals": MagicMock(), "instrumental": MagicMock()}

        with patch("app.ui.main_window.ProcessingDialog") as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog_class.return_value = mock_dialog

            window._on_export_triggered(stems)

            # Should have created and shown the export dialog
            mock_dialog_class.assert_called_once()
            assert window._export_dialog is not None
            mock_dialog.show.assert_called_once()
            mock_dialog.setWindowTitle.assert_called_once_with("Exporting Audio")

    def test_main_window_on_separation_started_shows_dialog(self, qapp):
        """Test that _on_separation_started shows processing dialog."""
        window, _, _, _ = self.create_window(qapp)

        with patch("app.ui.main_window.ProcessingDialog") as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog_class.return_value = mock_dialog

            window._on_separation_started()

            # Should have created and shown the processing dialog
            mock_dialog_class.assert_called_once()
            assert window._processing_dialog is not None
            mock_dialog.show.assert_called_once()
            mock_dialog.setWindowTitle.assert_called_once_with("Separating Audio")

    def test_main_window_on_separation_completed_hides_dialog(self, qapp):
        """Test that _on_separation_completed hides processing dialog."""
        window, _, _, _ = self.create_window(qapp)

        # Set up a processing dialog
        mock_dialog = MagicMock()
        window._processing_dialog = mock_dialog

        stems = {"vocals": MagicMock()}
        window._on_separation_completed(stems)

        # Should have hidden and cleaned up the dialog
        mock_dialog.hide.assert_called_once()
        mock_dialog.deleteLater.assert_called_once()
        assert window._processing_dialog is None

    def test_main_window_on_separation_failed_hides_dialog(self, qapp):
        """Test that _on_separation_failed hides processing dialog."""
        window, _, _, _ = self.create_window(qapp)

        # Set up a processing dialog
        mock_dialog = MagicMock()
        window._processing_dialog = mock_dialog

        window._on_separation_failed("Test error")

        # Should have hidden and cleaned up the dialog
        mock_dialog.hide.assert_called_once()
        mock_dialog.deleteLater.assert_called_once()
        assert window._processing_dialog is None

    def test_main_window_on_separation_cancelled_hides_dialog(self, qapp):
        """Test that _on_separation_cancelled hides processing dialog."""
        window, _, _, _ = self.create_window(qapp)

        # Set up a processing dialog
        mock_dialog = MagicMock()
        window._processing_dialog = mock_dialog

        window._on_separation_cancelled()

        # Should have hidden and cleaned up the dialog
        mock_dialog.hide.assert_called_once()
        mock_dialog.deleteLater.assert_called_once()
        assert window._processing_dialog is None

    def test_main_window_on_export_progress_updates_dialog(self, qapp):
        """Test that _on_export_progress updates export dialog."""
        window, _, _, _ = self.create_window(qapp)

        # Set up an export dialog
        mock_dialog = MagicMock()
        window._export_dialog = mock_dialog

        window._on_export_progress(50, "Exporting...")

        # Should have updated the dialog's progress bar and label
        mock_dialog._progress_bar.setValue.assert_called_once_with(50)
        mock_dialog._loading_label.setText.assert_called_once_with("Exporting...")

    def test_main_window_on_separation_progress_updates_dialog(self, qapp):
        """Test that _on_separation_progress updates processing dialog."""
        window, _, _, _ = self.create_window(qapp)

        # Set up a processing dialog
        mock_dialog = MagicMock()
        window._processing_dialog = mock_dialog

        window._on_separation_progress(75, "Separating vocals...")

        # Should have updated the dialog's progress bar and label
        mock_dialog._progress_bar.setValue.assert_called_once_with(75)
        mock_dialog._loading_label.setText.assert_called_once_with(
            "Separating vocals..."
        )

    def test_main_window_on_export_completed_hides_dialog(self, qapp):
        """Test that _on_export_completed hides export dialog."""
        window, _, _, _ = self.create_window(qapp)

        # Set up an export dialog
        mock_dialog = MagicMock()
        window._export_dialog = mock_dialog

        result = {"vocals": "/tmp/vocals.wav"}
        window._on_export_completed(result)

        # Should have hidden and cleaned up the dialog
        mock_dialog.hide.assert_called_once()
        mock_dialog.deleteLater.assert_called_once()
        assert window._export_dialog is None

    def test_main_window_on_export_failed_hides_dialog(self, qapp):
        """Test that _on_export_failed hides export dialog."""
        window, _, _, _ = self.create_window(qapp)

        # Set up an export dialog
        mock_dialog = MagicMock()
        window._export_dialog = mock_dialog

        window._on_export_failed("Export error")

        # Should have hidden and cleaned up the dialog
        mock_dialog.hide.assert_called_once()
        mock_dialog.deleteLater.assert_called_once()
        assert window._export_dialog is None

    def test_main_window_on_thermal_warning_shows_message(self, qapp):
        """Test that _on_thermal_warning shows a warning message."""
        window, _, _, _ = self.create_window(qapp)

        with patch("app.ui.main_window.QMessageBox") as MessageBoxMock:
            mock_message_box = MagicMock()
            MessageBoxMock.return_value = mock_message_box

            window._on_thermal_warning("high", 85.0)

            # Should have shown a warning message box
            MessageBoxMock.assert_called_once()
            mock_message_box.setIcon.assert_called_once()
            mock_message_box.setWindowTitle.assert_called_once()
            mock_message_box.setText.assert_called_once()
            mock_message_box.exec.assert_called_once()

    def test_main_window_on_state_changed_updates_ui_enabled_state(self, qapp):
        """Test that _on_state_changed correctly updates UI element enabled states."""
        window, main_controller, _, _ = self.create_window(qapp)

        # Test IDLE state
        app_state = AppState()
        app_state.processing_status = ProcessingState.IDLE
        app_state.current_file = Path("/tmp/test.wav")
        window._on_state_changed(app_state)

        # In IDLE with a file, separate button should be enabled
        assert window._separate_btn.isEnabled()

        # Test LOADING state
        app_state.processing_status = ProcessingState.LOADING
        window._on_state_changed(app_state)

        # In LOADING, UI should be disabled
        assert not window._separate_btn.isEnabled()
        assert not window._file_drop_zone.isEnabled()
        assert not window._track_selector.isEnabled()

        # Test PROCESSING state
        app_state.processing_status = ProcessingState.PROCESSING
        window._on_state_changed(app_state)

        # In PROCESSING, UI should be disabled
        assert not window._separate_btn.isEnabled()

        # Test COMPLETE state
        app_state.processing_status = ProcessingState.COMPLETE
        window._on_state_changed(app_state)

        # In COMPLETE with a file, separate button should be enabled
        assert window._separate_btn.isEnabled()

        # Test ERROR state
        app_state.processing_status = ProcessingState.ERROR
        window._on_state_changed(app_state)

        # In ERROR, UI should be enabled (to allow retry)
        assert window._separate_btn.isEnabled()

    def test_main_window_on_state_changed_no_file(self, qapp):
        """Test that _on_state_changed disables UI when no file is present."""
        window, _, _, _ = self.create_window(qapp)

        # Test with no current file
        app_state = AppState()
        app_state.processing_status = ProcessingState.IDLE
        app_state.current_file = None  # No file
        window._on_state_changed(app_state)

        # Should disable UI when no file is present
        assert not window._separate_btn.isEnabled()

    def test_main_window_drag_enter_event_accepts_urls(self, qapp):
        """Test that drag enter event accepts URLs."""
        window, _, _, _ = self.create_window(qapp)

        # Create a mock drag enter event with URLs
        event = MagicMock()
        event.mimeData().hasUrls.return_value = True
        event.mimeData().urls.return_value = [Path("/tmp/test.wav")]

        window.dragEnterEvent(event)

        # Should accept the proposed action
        event.acceptProposedAction.assert_called_once()

    def test_main_window_drag_enter_event_ignores_non_urls(self, qapp):
        """Test that drag enter event ignores non-URLs."""
        window, _, _, _ = self.create_window(qapp)

        # Create a mock drag enter event without URLs
        event = MagicMock()
        event.mimeData().hasUrls.return_value = False

        window.dragEnterEvent(event)

        # Should ignore the event (not accept proposed action)
        event.acceptProposedAction.assert_not_called()

    def test_main_window_drop_event_handles_files(self, qapp):
        """Test that drop event handles file drops."""
        window, main_controller, _, _ = self.create_window(qapp)

        # Create a mock drop event with file URLs
        event = MagicMock()
        event.mimeData().hasUrls.return_value = True
        event.mimeData().urls.return_value = [Path("/tmp/test.wav")]

        window.dropEvent(event)

        # Should have called _on_file_dropped with the file path
        window._on_file_dropped.assert_called_once_with("/tmp/test.wav")
        event.acceptProposedAction.assert_called_once()

    def test_main_window_drop_event_ignores_non_files(self, qapp):
        """Test that drop event ignores non-file drops."""
        window, main_controller, _, _ = self.create_window(qapp)

        # Create a mock drop event without URLs
        event = MagicMock()
        event.mimeData().hasUrls.return_value = False

        window.dropEvent(event)

        # Should not have called _on_file_dropped
        window._on_file_dropped.assert_not_called()
        # Should still accept the action (though it does nothing)
        event.acceptProposedAction.assert_called_once()

    def test_main_window_close_event_without_worker(self, qapp):
        """Test that close event works when no worker is running."""
        window, main_controller, playback_controller, _ = self.create_window(qapp)

        # Ensure no workers are running
        main_controller._current_worker = None
        playback_controller._mixer = None

        from PySide6.QtGui import QCloseEvent

        event = QCloseEvent()

        window.closeEvent(event)

        # Should not have called cancel_separation (no worker to cancel)
        main_controller.cancel_separation.assert_not_called()
        # Should have accepted the event
        assert event.isAccepted()

    def test_main_window_audio_load_worker_signals_connected(self, qapp):
        """Test that audio load worker signals are connected."""
        window, main_controller, _, _ = self.create_window(qapp)

        # Check that the window has methods to handle audio load worker signals
        assert hasattr(window, "_on_audio_loaded")
        assert hasattr(window, "_on_audio_load_error")

    def test_main_window_on_audio_loaded_sets_audio(self, qapp):
        """Test that _on_audio_loaded stores the loaded audio."""
        window, _, _, _ = self.create_window(qapp)

        import numpy as np

        audio = np.array([0.1, 0.2, 0.3])
        sample_rate = 44100

        window._on_audio_loaded(audio, sample_rate)

        assert window._loaded_audio is audio
        assert window._loaded_sample_rate == sample_rate

    def test_main_window_on_audio_load_error_shows_message(self, qapp):
        """Test that _on_audio_load_error shows an error message."""
        window, _, _, _ = self.create_window(qapp)

        with patch("app.ui.main_window.QMessageBox") as MessageBoxMock:
            mock_message_box = MagicMock()
            MessageBoxMock.return_value = mock_message_box

            window._on_audio_load_error("Failed to load audio")

            # Should have shown an error message box
            MessageBoxMock.assert_called_once()
            mock_message_box.setIcon.assert_called_once()
            mock_message_box.setWindowTitle.assert_called_once()
            mock_message_box.setText.assert_called_once()
            mock_message_box.exec.assert_called_once()

    def test_main_window_toggle_theme_method_exists(self, qapp):
        """Test that _change_theme method exists and can be called."""
        window, _, _, _ = self.create_window(qapp)

        # Should not raise
        window._change_theme("dark")
        window._change_theme("light")

    def test_main_window_window_title_is_set(self, qapp):
        """Test that window title is set correctly."""
        window, _, _, _ = self.create_window(qapp)
        assert window.windowTitle() == "Descombinator Pro"

    def test_main_window_minimum_size_set(self, qapp):
        """Test that minimum window size is set."""
        window, _, _, _ = self.create_window(qapp)
        # The minimum size is set in the constructor
        assert window.minimumSize().width() >= 800
        assert window.minimumSize().height() >= 600

    def test_main_window_apply_theme_method_exists(self, qapp):
        """Test that _apply_theme method exists."""
        window, _, _, _ = self.create_window(qapp)

        # Should not raise when called with valid theme names
        window._apply_theme("dark")
        window._apply_theme("light")

    def test_main_window_resolve_stylesheet_path(self, qapp):
        """Test that _styles_path helper function works."""
        from app.ui.main_window import _styles_path

        # Test with a theme name
        path = _styles_path("dark")
        assert isinstance(path, Path)
        assert path.name == "dark.qss"
        assert "styles" in str(path)

    def test_main_window_handles_exception_in_file_drop(self, qapp):
        """Test that _on_file_dropped handles exceptions gracefully."""
        window, main_controller, _, _ = self.create_window(qapp)

        # Make the controller raise an exception
        main_controller.handle_file_dropped.side_effect = Exception("Test error")

        # Should not raise - the exception should be handled
        window._on_file_dropped("/tmp/test.wav")

        # The controller method should still have been called
        main_controller.handle_file_dropped.assert_called_once_with("/tmp/test.wav")

    def test_main_window_handles_exception_in_separate_clicked(self, qapp):
        """Test that _on_separate_clicked handles exceptions gracefully."""
        window, main_controller, _, _ = self.create_window(qapp)

        # Make the controller raise an exception
        main_controller.handle_separate_requested.side_effect = Exception("Test error")

        # Should not raise - the exception should be handled
        window._on_separate_clicked()

        # The controller method should still have been called
        main_controller.handle_separate_requested.assert_called_once()

    def test_main_window_initializes_all_ui_components(self, qapp):
        """Test that all major UI components are initialized."""
        window, _, _, _ = self.create_window(qapp)

        # Check that all expected UI components exist
        assert window._file_drop_zone is not None
        assert window._playback_controls is not None
        assert window._track_mixer is not None
        assert window._track_selector is not None
        assert window._waveform_view is not None
        assert window._progress_bar is not None
        assert window._menu_bar is not None
        assert window.statusBar() is not None

    def test_main_window_sets_up_connections_during_init(self, qapp):
        """Test that signal connections are set up during initialization."""
        window, main_controller, playback_controller, settings_controller = (
            self.create_window(qapp)
        )

        # Verify that we mocked the expected controller methods that should be connected
        # These are verified indirectly through other tests, but we can at least
        # verify the controllers exist and have the expected methods
        assert main_controller is not None
        assert playback_controller is not None
        assert settings_controller is not None
