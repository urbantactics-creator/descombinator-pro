"""Modal progress dialog for separation processing."""

from __future__ import annotations

from PySide6.QtCore import QElapsedTimer, Qt, Signal, Slot
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)


class ProcessingDialog(QDialog):
    """Modal dialog showing separation progress with cancel button and ETA."""

    cancel_requested = Signal()

    def __init__(self, parent: object | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Processing Audio")
        self.setMinimumWidth(420)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._elapsed = QElapsedTimer()
        self._completed = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        self._message_label = QLabel("Initializing...")
        self._message_label.setWordWrap(True)
        layout.addWidget(self._message_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        layout.addWidget(self._progress_bar)

        self._eta_label = QLabel("ETA: calculating...")
        layout.addWidget(self._eta_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.clicked.connect(self._on_cancel)
        btn_layout.addWidget(self._cancel_btn)

        layout.addLayout(btn_layout)

    def start(self) -> None:
        """Start the elapsed timer and reset state."""
        self._completed = False
        self._elapsed.start()
        self._progress_bar.setValue(0)
        self._progress_bar.setStyleSheet("")
        self._message_label.setText("Starting separation...")
        self._eta_label.setText("ETA: calculating...")
        self._cancel_btn.setEnabled(True)

    @Slot(int, str)
    def update_progress(self, percent: int, message: str) -> None:
        """Update progress bar, message, and ETA."""
        elapsed_ms = self._elapsed.elapsed()
        if percent > 0:
            estimated_total = elapsed_ms * 100 / percent
            remaining_ms = max(0, int(estimated_total - elapsed_ms))
            self._eta_label.setText(f"ETA: {self._format_time(remaining_ms)}")
        self._progress_bar.setValue(percent)
        self._message_label.setText(message)

    def set_complete(self, message: str = "Separation complete!") -> None:
        """Display completion state."""
        self._completed = True
        self._progress_bar.setValue(100)
        self._progress_bar.setStyleSheet(
            "QProgressBar::chunk { background-color: #22C55E; }"
        )
        self._message_label.setText(message)
        self._eta_label.setText("Done")
        self._cancel_btn.setEnabled(False)

    def set_error(self, message: str) -> None:
        """Display error state."""
        self._completed = True
        self._progress_bar.setValue(0)
        self._progress_bar.setStyleSheet(
            "QProgressBar::chunk { background-color: #EF4444; }"
        )
        self._message_label.setText(f"Error: {message}")
        self._eta_label.setText("")
        self._cancel_btn.setText("Close")

    def set_cancelled(self) -> None:
        """Display cancelled state and close the dialog."""
        self._completed = True
        self._progress_bar.setValue(0)
        self._progress_bar.setStyleSheet(
            "QProgressBar::chunk { background-color: #F59E0B; }"
        )
        self._message_label.setText("Separation cancelled")
        self._eta_label.setText("")
        self._cancel_btn.setText("Close")
        self._cancel_btn.setEnabled(True)

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        if self._completed:
            self.accept()
            return
        self._cancel_btn.setEnabled(False)
        self._message_label.setText("Cancelling...")
        self.cancel_requested.emit()

    def reject(self) -> None:
        """Override reject to confirm cancellation."""
        if not self._completed:
            self._on_cancel()
            return
        super().reject()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        """Prevent closing while processing; trigger cancel instead."""
        if not self._completed:
            self._on_cancel()
            event.ignore()
            return
        event.accept()

    @staticmethod
    def _format_time(ms: int) -> str:
        """Format milliseconds as human-readable string."""
        total_secs = ms // 1000
        minutes = total_secs // 60
        seconds = total_secs % 60
        if minutes > 0:
            return f"{minutes}m {seconds:02d}s"
        return f"{seconds}s"
