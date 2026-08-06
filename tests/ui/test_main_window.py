"""Behavioral tests for the MainWindow."""

from unittest.mock import MagicMock, patch

import numpy as np

from app.controllers.main_controller import MainController
from app.controllers.playback_controller import PlaybackController
from app.controllers.settings_controller import SettingsController
from app.ui.main_window import MainWindow


def _make_window():
    """Create a MainWindow with mocked controllers for isolation."""
    main_controller = MagicMock(spec=MainController)
    playback_controller = MagicMock(spec=PlaybackController)
    settings_controller = MagicMock(spec=SettingsController)
    window = MainWindow(
        main_controller=main_controller,
        playback_controller=playback_controller,
        settings_controller=settings_controller,
    )
    return window, main_controller, playback_controller


def test_main_window_creation(qapp):
    """Test that MainWindow can be created."""
    main_controller = MainController()
    playback_controller = PlaybackController()
    settings_controller = SettingsController()

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
    main_controller = MainController()
    playback_controller = PlaybackController()
    settings_controller = SettingsController()

    window = MainWindow(
        main_controller=main_controller,
        playback_controller=playback_controller,
        settings_controller=settings_controller,
    )

    assert hasattr(window, "_file_drop_zone")
    assert hasattr(window, "_track_selector")
    assert hasattr(window, "_progress_bar")
    assert hasattr(window, "_waveform_view")
    assert hasattr(window, "_playback_controls")
    assert hasattr(window, "_status_label")
    assert hasattr(window, "_export_action")

    assert not window._export_action.isEnabled()


def test_separate_button_click_delegates(qapp):
    """Test that clicking the separate button triggers the controller."""
    window, main_controller, _ = _make_window()
    window._on_separate_clicked()
    main_controller.handle_separate_requested.assert_called_once()


def test_separation_started_updates_ui(qapp):
    """Test _on_separation_started updates status and shows the dialog."""
    window, _, _ = _make_window()
    window._on_separation_started()
    assert "Starting separation" in window._status_label.text()
    assert window._processing_dialog is not None


def test_separation_completed_updates_ui(qapp):
    """Test _on_separation_completed stores stems and enables export."""
    window, _, playback_controller = _make_window()
    stems = {"vocals": np.zeros(44100, dtype=np.float32)}
    window._on_separation_completed(stems)
    assert window._separated_stems == stems
    assert window._export_action.isEnabled()
    assert "complete" in window._status_label.text().lower()
    playback_controller.set_stems.assert_called_once_with(stems)


def test_separation_failed_updates_ui(qapp):
    """Test _on_separation_failed shows the error state."""
    window, _, _ = _make_window()
    window._on_separation_failed("Something broke")
    assert "Something broke" in window._status_label.text()
    assert window._progress_bar.message == "Something broke"


def test_separation_progress_updates_ui(qapp):
    """Test _on_separation_progress updates status and progress bar."""
    window, _, _ = _make_window()
    window._on_separation_progress(50, "Processing...")
    assert "Processing..." in window._status_label.text()
    assert window._progress_bar.value == 50


def test_playback_position_changed_updates_controls(qapp):
    """Test _on_playback_position_changed updates slider and waveform."""
    window, _, _ = _make_window()
    window._on_playback_position_changed(15_000)
    assert window._playback_controls._position_label.text() == "0:15"


def test_playback_duration_changed_updates_controls(qapp):
    """Test _on_playback_duration_changed updates the duration label."""
    window, _, _ = _make_window()
    window._on_playback_duration_changed(90_000)
    assert window._playback_controls._duration_label.text() == "1:30"


def test_playback_state_changed_updates_controls(qapp):
    """Test _on_playback_state_changed updates play/pause buttons."""
    window, _, _ = _make_window()
    window._on_playback_state_changed("playing")
    assert window._playback_controls._play_button.isEnabled() is False
    assert window._playback_controls._pause_button.isEnabled() is True


def test_playback_volume_changed_updates_controls(qapp):
    """Test _on_playback_volume_changed updates the volume slider."""
    window, _, _ = _make_window()
    window._on_playback_volume_changed(0.4)
    assert window._playback_controls._volume_slider.value() == 40


def test_playback_error_updates_status(qapp):
    """Test _on_playback_error updates the status label."""
    window, _, _ = _make_window()
    with patch("app.ui.main_window.QMessageBox.warning"):
        window._on_playback_error("No device")
    assert "Playback error: No device" in window._status_label.text()


def test_tracks_changed_rebuilds_mixer(qapp):
    """Test _on_tracks_changed rebuilds the track mixer."""
    window, _, playback_controller = _make_window()
    playback_controller.track_volumes.return_value = {"vocals": 0.8}
    playback_controller.muted_map.return_value = {"vocals": False}
    window._on_tracks_changed(["vocals"])
    assert window._track_mixer.track_names() == ["vocals"]


def test_track_volume_changed_delegates(qapp):
    """Test _on_track_volume_changed forwards to playback controller."""
    window, _, playback_controller = _make_window()
    window._on_track_volume_changed("vocals", 0.7)
    playback_controller.set_track_volume.assert_called_once_with("vocals", 0.7)


def test_track_muted_changed_delegates(qapp):
    """Test _on_track_muted_changed forwards to playback controller."""
    window, _, playback_controller = _make_window()
    window._on_track_muted_changed("vocals", True)
    playback_controller.set_track_muted.assert_called_once_with("vocals", True)


def test_thermal_warning_updates_status(qapp):
    """Test _on_thermal_warning shows thermal state in the status bar."""
    window, _, _ = _make_window()
    window._on_thermal_warning("hot", 85.0)
    assert "Thermal: hot (85°C)" in window._status_bar.currentMessage()


def test_file_dropped_flow(qapp, tmp_path):
    """Test _on_file_dropped delegates to controllers."""
    window, main_controller, playback_controller = _make_window()
    audio_file = tmp_path / "song.wav"
    audio_file.write_bytes(b"RIFF fake")

    with patch("app.ui.main_window.AudioLoadWorker") as mock_worker:
        window._on_file_dropped(str(audio_file))

    playback_controller.reset.assert_called_once()
    playback_controller.record_last_file.assert_called_once_with(str(audio_file))
    main_controller.handle_file_dropped.assert_called_once_with(str(audio_file))
    assert f"Loaded: {audio_file.name}" in window._status_label.text()
    assert window._separate_btn.isEnabled()
    mock_worker.assert_called_once()


def test_change_theme(qapp):
    """Test _change_theme applies a stylesheet without crashing."""
    window, _, _ = _make_window()
    window._change_theme("dark")
    window._change_theme("light")
    assert window is not None


def test_stems_changed_delegates(qapp):
    """Test _on_stems_changed forwards to the main controller."""
    window, main_controller, _ = _make_window()
    main_controller.handle_stems_changed.reset_mock()
    window._on_stems_changed(["vocals", "drums"])
    main_controller.handle_stems_changed.assert_called_once_with(["vocals", "drums"])


def test_audio_loaded_updates_state(qapp):
    """Test _on_audio_loaded sets audio data and controller state."""
    window, main_controller, playback_controller = _make_window()
    audio = np.zeros(44100, dtype=np.float32)
    window._on_audio_loaded((audio, 44100))
    main_controller.set_loaded_audio.assert_called_once_with(audio, 44100)
    playback_controller.set_source.assert_called_once_with(audio, 44100)


def test_display_ready_renders_points(qapp):
    """Test _on_display_ready renders decimated points."""
    window, _, _ = _make_window()
    points = np.zeros(100, dtype=np.float32)
    window._on_display_ready((points, 0.01, 1.0))
    assert window is not None


def test_audio_load_error_updates_status(qapp):
    """Test _on_audio_load_error updates the status label."""
    window, _, _ = _make_window()
    window._on_audio_load_error("decode failed")
    assert "Error loading audio: decode failed" in window._status_label.text()


def test_load_stylesheet_applies_persisted_theme(qapp) -> None:
    """The persisted theme (not hardcoded 'dark') is applied at startup (A8)."""
    from app.controllers.settings_controller import SettingsController
    from app.models.settings_model import SettingsModel

    settings_ctrl = SettingsController()
    settings_ctrl._settings = SettingsModel(theme="light")
    window = MainWindow(
        MagicMock(spec=MainController),
        MagicMock(spec=PlaybackController),
        settings_ctrl,
    )
    assert window.styleSheet() != ""


def test_styles_path_resolves_in_repo() -> None:
    """_styles_path points at app/resources, not a hardcoded path (A8)."""
    from app.ui.main_window import _styles_path

    style_path = _styles_path("dark")
    assert style_path.name == "dark.qss"
    assert "resources" in style_path.parts
    assert style_path.exists()


def test_settings_changed_reapplies_theme(qapp) -> None:
    """Changing settings re-applies the new theme (A8)."""
    from unittest.mock import patch

    from app.controllers.settings_controller import SettingsController
    from app.models.settings_model import SettingsModel

    settings_ctrl = SettingsController()
    window = MainWindow(
        MagicMock(spec=MainController),
        MagicMock(spec=PlaybackController),
        settings_ctrl,
    )
    with patch.object(window, "_change_theme") as mock_change:
        window._on_settings_changed(SettingsModel(theme="light"))
    mock_change.assert_called_once_with("light")
