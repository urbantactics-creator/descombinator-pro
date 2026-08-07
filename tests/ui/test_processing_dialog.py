"""Behavioral tests for the ProcessingDialog."""

from PySide6.QtWidgets import QDialog

from app.ui.processing_dialog import ProcessingDialog


def _make_dialog(qapp):
    return ProcessingDialog()


def test_processing_dialog_creation(qapp):
    """Test that ProcessingDialog can be created."""
    dialog = _make_dialog(qapp)
    assert dialog is not None
    assert dialog.windowTitle() == "Processing..."
    assert dialog._progress_bar.value() == 0


def test_processing_dialog_update_progress(qapp):
    """Test update_progress updates the bar and message."""
    dialog = _make_dialog(qapp)
    dialog.update_progress(50, "Separating vocals...")
    assert dialog._progress_bar.value() == 50
    assert dialog._loading_label.text() == "Separating vocals..."


def test_processing_dialog_set_error(qapp):
    """Test set_error displays the error state."""
    dialog = _make_dialog(qapp)
    dialog.set_error("Failed")
    assert "Error: Failed" in dialog._loading_label.text()
    assert dialog._progress_bar.value() == 0


def test_processing_dialog_set_cancelled(qapp):
    """Test set_cancelled displays the cancellation state."""
    dialog = _make_dialog(qapp)
    dialog.set_cancelled()
    assert dialog._loading_label.text() == "Operation cancelled"
    assert dialog._progress_bar.value() == 0


def test_processing_dialog_set_complete_stops_animations(qapp):
    """Test set_complete stops the looping animation and timer, then accepts."""
    dialog = _make_dialog(qapp)
    dialog.set_complete()
    assert dialog.result() == QDialog.Accepted
    assert dialog._icon_timer.isActive() is False


def test_processing_dialog_close_stops_animations(qapp):
    """Test closing the dialog stops the looping animation and timer."""
    from PySide6.QtGui import QCloseEvent

    dialog = _make_dialog(qapp)
    dialog.closeEvent(QCloseEvent())
    assert dialog._icon_timer.isActive() is False


def test_processing_dialog_reject_stops_animations(qapp):
    """Test reject stops animations and yields a Rejected result."""
    dialog = _make_dialog(qapp)
    dialog.reject()
    assert dialog.result() == QDialog.Rejected
    assert dialog._icon_timer.isActive() is False
