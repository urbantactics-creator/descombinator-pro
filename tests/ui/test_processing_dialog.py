"""Behavioral tests for the ProcessingDialog."""

from app.ui.processing_dialog import ProcessingDialog


def _make_dialog(qapp):
    return ProcessingDialog()


def test_processing_dialog_creation(qapp):
    """Test that ProcessingDialog can be created."""
    dialog = _make_dialog(qapp)
    assert dialog is not None
    assert dialog.windowTitle() == "Processing Audio"


def test_processing_dialog_start(qapp):
    """Test start resets the dialog state."""
    dialog = _make_dialog(qapp)
    dialog.start()
    assert dialog._progress_bar.value() == 0
    assert dialog._message_label.text() == "Starting separation..."
    assert "calculating" in dialog._eta_label.text()
    assert dialog._cancel_btn.isEnabled()


def test_processing_dialog_update_progress(qapp):
    """Test update_progress updates the bar, message, and ETA."""
    dialog = _make_dialog(qapp)
    dialog.start()
    dialog.update_progress(50, "Processing...")
    assert dialog._progress_bar.value() == 50
    assert dialog._message_label.text() == "Processing..."
    assert "ETA" in dialog._eta_label.text()


def test_processing_dialog_set_complete(qapp):
    """Test set_complete displays the completion state."""
    dialog = _make_dialog(qapp)
    dialog.start()
    dialog.set_complete()
    assert dialog._progress_bar.value() == 100
    assert dialog._eta_label.text() == "Done"
    assert not dialog._cancel_btn.isEnabled()


def test_processing_dialog_set_error(qapp):
    """Test set_error displays the error state."""
    dialog = _make_dialog(qapp)
    dialog.start()
    dialog.set_error("Failed")
    assert "Error: Failed" in dialog._message_label.text()
    assert dialog._cancel_btn.text() == "Close"


def test_processing_dialog_cancel_emits(qapp):
    """Test cancel button emits cancel_requested."""
    dialog = _make_dialog(qapp)
    dialog.start()
    emitted = []
    dialog.cancel_requested.connect(lambda: emitted.append(1))
    dialog._on_cancel()
    assert emitted == [1]
    assert not dialog._cancel_btn.isEnabled()
    assert dialog._message_label.text() == "Cancelling..."


def test_processing_dialog_reject_after_complete(qapp):
    """Test reject closes normally after completion without cancel flow."""
    dialog = _make_dialog(qapp)
    dialog.start()
    dialog.set_complete()
    emitted = []
    dialog.cancel_requested.connect(lambda: emitted.append(1))
    dialog.reject()
    # Regression (C5): the previous `or True` made this a tautology.
    assert dialog.result() == dialog.DialogCode.Rejected
    assert emitted == []


def test_processing_dialog_format_time(qapp):
    """Test the human-readable time formatting."""
    assert ProcessingDialog._format_time(0) == "0s"
    assert ProcessingDialog._format_time(30_000) == "30s"
    assert ProcessingDialog._format_time(90_000) == "1m 30s"
    assert ProcessingDialog._format_time(3_600_000) == "60m 00s"
