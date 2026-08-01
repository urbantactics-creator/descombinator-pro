"""Progress bar widget for separation status."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QWidget


class ProgressBar(QWidget):
    """Widget showing separation progress and status message."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(True)
        layout.addWidget(self._bar)

        self._message = QLabel("Ready")
        self._message.setAlignment(Qt.AlignLeft)
        layout.addWidget(self._message)

        layout.addStretch()

    def set_progress(self, value: int, message: str = "") -> None:
        self._bar.setValue(max(0, min(100, value)))
        if message:
            self._message.setText(message)

    def reset(self) -> None:
        self._bar.setValue(0)
        self._message.setText("Ready")

    @property
    def value(self) -> int:
        return self._bar.value()

    @property
    def message(self) -> str:
        return self._message.text()
