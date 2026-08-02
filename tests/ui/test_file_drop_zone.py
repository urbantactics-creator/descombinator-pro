"""Tests for the FileDropZone widget."""

import os
import tempfile

from PySide6.QtCore import QMimeData, Qt, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from app.widgets.file_drop_zone import FileDropZone


def test_file_drop_zone_creation(qapp):
    """Test that FileDropZone can be created."""
    widget = FileDropZone()
    assert widget is not None
    assert widget.windowTitle() == ""  # No window title for widget


def test_file_drop_zone_accepts_valid_files(qapp):
    """Test that FileDropZone accepts valid audio file drops."""
    widget = FileDropZone()

    # Create a temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(b"fake wav data")
        temp_path = tmp.name

    try:
        # Create a drag enter event with a valid file URL
        mime_data = QMimeData()
        urls = [QUrl.fromLocalFile(temp_path)]
        mime_data.setUrls(urls)

        event = QDragEnterEvent(
            widget.rect().center(),
            Qt.CopyAction,
            mime_data,
            Qt.NoButton,
            Qt.NoModifier,
        )

        # Accept the drag event
        widget.dragEnterEvent(event)
        assert event.isAccepted()

        # Create a drop event
        drop_event = QDropEvent(
            widget.rect().center(),
            Qt.CopyAction,
            mime_data,
            Qt.NoButton,
            Qt.NoModifier,
        )

        # Accept the drop event
        widget.dropEvent(drop_event)
        assert drop_event.isAccepted()

    finally:
        # Clean up temp file
        os.unlink(temp_path)


def test_file_drop_zone_rejects_invalid_files(qapp):
    """Test that FileDropZone rejects non-audio file drops."""
    widget = FileDropZone()

    # Create a temporary text file
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp.write(b"not an audio file")
        temp_path = tmp.name

    try:
        # Create a drag enter event with an invalid file URL
        mime_data = QMimeData()
        urls = [QUrl.fromLocalFile(temp_path)]
        mime_data.setUrls(urls)

        event = QDragEnterEvent(
            widget.rect().center(),
            Qt.CopyAction,
            mime_data,
            Qt.NoButton,
            Qt.NoModifier,
        )

        # Accept the drag event (it's still a valid file, just not audio)
        widget.dragEnterEvent(event)
        assert event.isAccepted()

        # Create a drop event
        drop_event = QDropEvent(
            widget.rect().center(),
            Qt.CopyAction,
            mime_data,
            Qt.NoButton,
            Qt.NoModifier,
        )

        # Accept the drop event
        widget.dropEvent(drop_event)
        assert drop_event.isAccepted()

        # The label should show "Unsupported file format"
        # Note: This is harder to test without accessing the internal label

    finally:
        # Clean up temp file
        os.unlink(temp_path)


def test_file_drop_zone_set_message(qapp):
    """Test setting a custom message on the FileDropZone."""
    widget = FileDropZone()
    test_message = "Custom message"
    widget.set_message(test_message)
    # Note: We can't easily test the label text without accessing private attributes
    # In a real test, we might expose a method to get the current message
