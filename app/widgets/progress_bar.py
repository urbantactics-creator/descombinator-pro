"""Progress bar widget for separation status."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QWidget


class ProgressBar(QWidget):
    """Widget showing separation progress and status message."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create the progress bar and status label."""
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
        """Update progress value and optional status message."""
        self._bar.setValue(max(0, min(100, value)))
        if message:
            self._message.setText(message)

    def reset(self) -> None:
        """Reset the progress bar to the initial ready state."""
        self._bar.setValue(0)
        self._bar.setFormat("%p%")
        self._bar.setStyleSheet("")
        self._message.setText("Ready")

    def set_error(self, message: str) -> None:
        """Display error state with message."""
        self._bar.setValue(0)
        self._bar.setFormat(f"Error: {message}")
        self._bar.setStyleSheet("QProgressBar::chunk { background-color: #EF4444; }")
        self._message.setText(message)

    @property
    def value(self) -> int:
        """Current progress value."""
        return self._bar.value()

    @property
    def message(self) -> str:
        """Current status message."""
        return self._message.text()
