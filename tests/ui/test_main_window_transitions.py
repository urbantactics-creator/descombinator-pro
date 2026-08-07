"""Integration tests for MainWindow's transition-effect wiring."""

from unittest.mock import MagicMock

from PySide6.QtCore import QAbstractAnimation

from app.controllers.main_controller import MainController
from app.controllers.playback_controller import PlaybackController
from app.controllers.settings_controller import SettingsController
from app.models.app_state import AppState
from app.models.settings_model import SettingsModel
from app.ui.main_window import MainWindow
from app.ui.processing_dialog import ProcessingDialog
from app.widgets.file_drop_zone import FileDropZone


def _make_window() -> MainWindow:
    main_controller = MagicMock(spec=MainController)
    main_controller._app_state = AppState()
    playback_controller = MagicMock(spec=PlaybackController)
    settings_controller = MagicMock(spec=SettingsController)
    settings_controller.settings = SettingsModel()
    return MainWindow(main_controller, playback_controller, settings_controller)


def _cleanup_window(window: MainWindow) -> None:
    for dialog in (window._processing_dialog, window._export_dialog):
        if dialog is not None:
            if getattr(dialog, "_progress_anim", None) is not None:
                dialog._progress_anim.stop()
            if getattr(dialog, "_icon_timer", None) is not None:
                dialog._icon_timer.stop()
            dialog.close()
            dialog.deleteLater()
    window._processing_dialog = None
    window._export_dialog = None
    window.deleteLater()


def test_main_window_owns_file_drop_zone_with_transitions(qapp):
    window = _make_window()
    try:
        assert isinstance(window._file_drop_zone, FileDropZone)
        assert window._file_drop_zone._enter_anim is not None
        assert window._file_drop_zone._exit_anim is not None
        assert window._file_drop_zone._opacity_anim is not None
    finally:
        _cleanup_window(window)


def test_main_window_processing_dialog_progress_animation_starts(qapp):
    window = _make_window()
    try:
        dialog = ProcessingDialog(window)
        window._processing_dialog = dialog
        dialog.show()
        assert dialog._progress_anim is not None
        assert dialog._progress_anim.duration() == 2000
        assert dialog._progress_anim.state() == QAbstractAnimation.Running
    finally:
        _cleanup_window(window)


def test_main_window_export_dialog_progress_animation_starts(qapp):
    window = _make_window()
    try:
        dialog = ProcessingDialog(window)
        window._export_dialog = dialog
        dialog.setWindowTitle("Exporting Audio")
        dialog.show()
        assert dialog._progress_anim is not None
        assert dialog._progress_anim.duration() == 2000
        assert dialog._progress_anim.state() == QAbstractAnimation.Running
    finally:
        _cleanup_window(window)


def test_main_window_progress_update_reflects_separation(qapp):
    window = _make_window()
    try:
        dialog = ProcessingDialog(window)
        window._processing_dialog = dialog
        dialog.show()
        window._on_separation_progress(75, "Separating vocals...")
        assert window._processing_dialog._progress_bar.value() == 75
        assert window._processing_dialog._loading_label.text() == "Separating vocals..."
    finally:
        _cleanup_window(window)
