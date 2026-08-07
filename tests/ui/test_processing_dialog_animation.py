"""Focused unit tests for ProcessingDialog animation features."""

from PySide6.QtCore import QAbstractAnimation, QEasingCurve
from PySide6.QtGui import QCloseEvent

from app.ui.processing_dialog import ProcessingDialog

_EXPECTED_LOADING_STATES = {"Processing audio...", "Processing audio... "}


def _stop_animations(dialog):
    dialog._progress_anim.stop()
    dialog._icon_timer.stop()


def test_progress_anim_configured(qapp):
    dialog = ProcessingDialog()
    try:
        anim = dialog._progress_anim
        assert anim.duration() == 2000
        assert anim.loopCount() == -1
        assert anim.easingCurve().type() == QEasingCurve.InOutQuad
        assert anim.startValue() == 0
        assert anim.endValue() == 100
        assert anim.state() == QAbstractAnimation.Running
    finally:
        _stop_animations(dialog)
        dialog.close()


def test_icon_timer_configured(qapp):
    dialog = ProcessingDialog()
    try:
        assert dialog._icon_timer.interval() == 100
        assert dialog._icon_timer.isActive() is True
    finally:
        _stop_animations(dialog)
        dialog.close()


def test_update_progress(qapp):
    dialog = ProcessingDialog()
    try:
        dialog.update_progress(50, "Working...")
        assert dialog._progress_bar.value() == 50
        assert dialog._loading_label.text() == "Working..."
    finally:
        _stop_animations(dialog)
        dialog.close()


def test_rotate_icon_keeps_label_in_expected_set(qapp):
    dialog = ProcessingDialog()
    try:
        before = dialog._loading_label.text()
        assert before in _EXPECTED_LOADING_STATES
        dialog._rotate_icon()
        dialog._rotate_icon()
        assert dialog._loading_label.text() in _EXPECTED_LOADING_STATES
    finally:
        _stop_animations(dialog)
        dialog.close()


def test_set_complete_stops_animations(qapp):
    dialog = ProcessingDialog()
    try:
        dialog.set_complete()
        assert dialog._progress_anim.state() == QAbstractAnimation.Stopped
        assert dialog._icon_timer.isActive() is False
    finally:
        _stop_animations(dialog)
        dialog.close()


def test_close_event_stops_animations(qapp):
    dialog = ProcessingDialog()
    try:
        dialog._progress_anim.start()
        dialog._icon_timer.start()
        assert dialog._progress_anim.state() == QAbstractAnimation.Running
        assert dialog._icon_timer.isActive() is True
        dialog.closeEvent(QCloseEvent())
        assert dialog._progress_anim.state() == QAbstractAnimation.Stopped
        assert dialog._icon_timer.isActive() is False
    finally:
        dialog.close()


def test_set_error_sets_message(qapp):
    dialog = ProcessingDialog()
    try:
        dialog.set_error("Failed")
        assert "Error: Failed" in dialog._loading_label.text()
        assert dialog._progress_bar.value() == 0
    finally:
        _stop_animations(dialog)
        dialog.close()


def test_set_cancelled_sets_message(qapp):
    dialog = ProcessingDialog()
    try:
        dialog.set_cancelled()
        assert dialog._loading_label.text() == "Operation cancelled"
        assert dialog._progress_bar.value() == 0
    finally:
        _stop_animations(dialog)
        dialog.close()
