"""Accessibility option tests."""

from unittest.mock import MagicMock

from PySide6.QtCore import QAbstractAnimation

from app.controllers.main_controller import MainController
from app.controllers.playback_controller import PlaybackController
from app.controllers.settings_controller import SettingsController
from app.models.app_state import AppState
from app.models.settings_model import SettingsModel
from app.ui.main_window import MainWindow
from app.ui.processing_dialog import ProcessingDialog


def _make_window(reduced_motion=False, high_contrast=False):
    main_controller = MagicMock(spec=MainController)
    main_controller._app_state = AppState()
    main_controller._current_worker = None
    playback_controller = MagicMock(spec=PlaybackController)
    settings_controller = MagicMock(spec=SettingsController)
    settings = SettingsModel(reduced_motion=reduced_motion, high_contrast=high_contrast)
    settings_controller.settings = settings
    window = MainWindow(main_controller, playback_controller, settings_controller)
    window._processing_dialog = ProcessingDialog(window)
    window._apply_accessibility()
    return window


def _cleanup_window(window):
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
    window.close()
    window.deleteLater()


def test_reduced_motion_disables_file_drop_zone_animations(qapp):
    window = _make_window(reduced_motion=True)
    try:
        assert window._file_drop_zone._reduced_motion is True
        window._file_drop_zone._apply_drag_style(True, valid=True)
        assert window._file_drop_zone._label.text() == "Drop to load audio file"
        assert window._file_drop_zone._enter_anim.state() == QAbstractAnimation.Stopped
    finally:
        _cleanup_window(window)


def test_reduced_motion_disables_processing_dialog_animations(qapp):
    window = _make_window(reduced_motion=True)
    try:
        assert window._processing_dialog._reduced_motion is True
        assert (
            window._processing_dialog._progress_anim.state()
            == QAbstractAnimation.Stopped
        )
        assert window._processing_dialog._icon_timer.isActive() is False
    finally:
        _cleanup_window(window)


def test_high_contrast_applies_override(qapp):
    window = _make_window(high_contrast=True)
    try:
        assert "high_contrast" in window.styleSheet() or window.styleSheet() != ""
    finally:
        _cleanup_window(window)
