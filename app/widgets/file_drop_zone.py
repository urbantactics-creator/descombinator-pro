"""File drop zone widget for drag-and-drop audio files."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from engine.audio.loader import AudioLoader


class FileDropZone(QWidget):
    """Widget that accepts drag-and-drop of audio files."""

    file_dropped = Signal(str)

    SUPPORTED_FORMATS = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".aiff"}

    def __init__(self) -> None:
        super().__init__()
        self._loader = AudioLoader()
        self._setup_ui()

    def _setup_ui(self) -> None:
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

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if self._has_valid_urls(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if self._is_supported(file_path):
                self.file_dropped.emit(file_path)
            else:
                self._label.setText("Unsupported file format")

    def _has_valid_urls(self, event: QDragEnterEvent) -> bool:
        urls = event.mimeData().urls()
        return len(urls) > 0 and urls[0].isLocalFile()

    def _is_supported(self, file_path: str) -> bool:
        path = Path(file_path)
        return path.suffix.lower() in self.SUPPORTED_FORMATS

    def set_message(self, message: str) -> None:
        self._label.setText(message)
