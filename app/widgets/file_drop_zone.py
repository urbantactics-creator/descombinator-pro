"""File drop zone widget for drag-and-drop audio files.

This widget provides an interactive area for users to drag and drop audio files.
It includes animated visual feedback for drag enter/leave events and validates
file formats before accepting drops.

Example:
    >>> drop_zone = FileDropZone()
    >>> drop_zone.file_dropped.connect(on_file_dropped)
    >>> drop_zone.set_message("Drop your audio file here")
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDragEvent, QDropEvent
from PySide6.QtWidgets import QGraphicsOpacityEffect, QLabel, QVBoxLayout, QWidget


class FileDropZone(QWidget):
    """Widget that accepts drag-and-drop of audio files.

    Provides animated visual feedback during drag operations:
    - Green background for supported audio formats
    - Red background for unsupported formats
    - Smooth transitions between states

    Attributes:
        file_dropped: Signal emitted with the file path when a valid audio
        file is dropped.
        SUPPORTED_FORMATS: Set of supported audio file extensions.
    """

    file_dropped = Signal(str)

    SUPPORTED_FORMATS = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".aiff"}

    def __init__(self) -> None:
        """Initialize the file drop zone with UI and animations."""
        super().__init__()
        self._setup_ui()
        self._is_drag_enter = False
        self._setup_animations()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self._label = QLabel("Drag & drop an audio file here")
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet(
            "border: 2px dashed #888; padding: 20px; border-radius: 8px;"
        )
        layout.addWidget(self._label)

    def _setup_animations(self) -> None:
        """Configure animations for drag enter/leave transitions."""
        self._enter_anim = QPropertyAnimation(self._label, b"styleSheet")
        self._enter_anim.setDuration(200)
        self._enter_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._exit_anim = QPropertyAnimation(self._label, b"styleSheet")
        self._exit_anim.setDuration(150)
        self._exit_anim.setEasingCurve(QEasingCurve.InCubic)

        self._opacity_effect = QGraphicsOpacityEffect(self._label)
        self._label.setGraphicsEffect(self._opacity_effect)
        self._opacity_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._opacity_anim.setDuration(200)

    def _apply_drag_style(self, entered: bool, valid: bool = True) -> None:
        """Apply visual feedback for drag enter/leave events.

        Args:
            entered: True if drag entered the widget, False if left.
            valid: True if the dragged file is a supported format.
        """
        if entered:
            if valid:
                style = (
                    "border: 2px solid #4CAF50; "
                    "padding: 20px; "
                    "border-radius: 8px; "
                    "background-color: #f1f8e9;"
                )
                self._label.setText("Drop to load audio file")
            else:
                style = (
                    "border: 2px solid #f44336; "
                    "padding: 20px; "
                    "border-radius: 8px; "
                    "background-color: #fdeaea;"
                )
                self._label.setText("Unsupported format")
        else:
            style = (
                "border: 2px dashed #888; "
                "padding: 20px; "
                "border-radius: 8px; "
                "background-color: transparent;"
            )
            self._label.setText("Drag & drop an audio file here")

        self._enter_anim.stop()
        self._exit_anim.stop()
        anim = self._enter_anim if entered else self._exit_anim
        anim.setStartValue(self._label.styleSheet())
        anim.setEndValue(style)
        anim.start()

        self._opacity_anim.stop()
        self._opacity_anim.setStartValue(self._opacity_effect.opacity())
        self._opacity_anim.setEndValue(1.0)
        self._opacity_anim.start()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Accept drag events that contain local audio file URLs.

        Args:
            event: The drag enter event containing MIME data.
        """
        if self._has_valid_urls(event):
            file_path = event.mimeData().urls()[0].toLocalFile()
            if self._is_supported(file_path):
                self._apply_drag_style(True, valid=True)
                event.acceptProposedAction()
            else:
                self._apply_drag_style(True, valid=False)
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle dropped files and emit file_dropped for supported audio.

        Args:
            event: The drop event containing MIME data with file URLs.
        """
        self._apply_drag_style(False)
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if self._is_supported(file_path):
                self.file_dropped.emit(file_path)
            else:
                self._label.setText("Unsupported file format")
        event.acceptProposedAction()

    def dragLeaveEvent(self, event: QDragEvent) -> None:
        """Reset visual state when drag leaves.

        Args:
            event: The drag leave event.
        """
        self._apply_drag_style(False)
        event.ignore()

    def _has_valid_urls(self, event: QDragEnterEvent) -> bool:
        """Check whether the drag event contains local file URLs.

        Args:
            event: The drag enter event to check.

        Returns:
            True if the event contains at least one local file URL.
        """
        urls = event.mimeData().urls()
        return len(urls) > 0 and urls[0].isLocalFile()

    def _is_supported(self, file_path: str) -> bool:
        """Check whether the file extension is a supported audio format.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the file extension is in SUPPORTED_FORMATS.
        """
        path = Path(file_path)
        return path.suffix.lower() in self.SUPPORTED_FORMATS

    def set_message(self, message: str) -> None:
        """Update the drop zone prompt text.

        Args:
            message: The new message to display.
        """
        self._label.setText(message)
