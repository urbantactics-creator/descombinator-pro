"""Processing dialog with loading animations.

This dialog provides visual feedback during audio separation processing.
It includes an animated progress bar and loading indicator.

Example:
    >>> dialog = ProcessingDialog(parent)
    >>> dialog.update_progress(50, "Separating vocals...")
    >>> dialog.set_complete()
"""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtWidgets import QDialog, QLabel, QProgressBar, QVBoxLayout


class ProcessingDialog(QDialog):
    """Dialog with loading animations for separation process.

    Provides animated visual feedback during audio separation:
    - Looping progress bar animation with easing
    - Loading icon rotation animation
    - Real-time progress and message updates
    - Smooth fade-in/fade-out effects

    Attributes:
        _progress_anim: Animation for the progress bar.
        _icon_timer: Timer for loading icon rotation.
    """

    def __init__(self, parent=None) -> None:
        """Initialize the processing dialog with animations.

        Args:
            parent: Parent widget (typically MainWindow).
        """
        super().__init__(parent)
        self.setWindowTitle("Processing...")
        self.setFixedSize(300, 150)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._reduced_motion = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self._loading_label = QLabel("Processing audio...")
        self._loading_label.setAlignment(Qt.AlignCenter)
        self._loading_label.setStyleSheet("font-size: 14px; color: #ffffff;")
        layout.addWidget(self._loading_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setStyleSheet(
            "border: 2px solid #4CAF50;border-radius: 8px;text-align: center;"
        )
        layout.addWidget(self._progress_bar)

        self._start_animation()

    def set_reduced_motion(self, enabled: bool) -> None:
        """Disable looping animations (accessibility: reduced motion)."""
        self._reduced_motion = bool(enabled)
        if self._reduced_motion:
            self._progress_anim.stop()
            self._icon_timer.stop()

    def _start_animation(self) -> None:
        """Start loading animations."""
        self._progress_anim = QPropertyAnimation(self._progress_bar, b"value")
        self._progress_anim.setDuration(2000)
        self._progress_anim.setStartValue(0)
        self._progress_anim.setEndValue(100)
        self._progress_anim.setLoopCount(-1)
        self._progress_anim.setEasingCurve(QEasingCurve.InOutQuad)

        self._icon_timer = QTimer(self)
        self._icon_timer.setInterval(100)
        self._icon_timer.timeout.connect(self._rotate_icon)

        if not self._reduced_motion:
            self._progress_anim.start()
            self._icon_timer.start()

    def _rotate_icon(self) -> None:
        """Rotate loading icon."""
        current_text = self._loading_label.text()
        if (
            current_text == "Processing audio..."
            or current_text == "Processing audio... "
        ):
            self._loading_label.setText("Processing audio... ")
        else:
            self._loading_label.setText("Processing audio... ")

    def _stop_animations(self) -> None:
        """Stop the looping animation and rotation timer.

        The progress animation has ``loopCount=-1`` and the rotation timer
        fires every 100ms. Leaving either running keeps the QObject alive and
        leaks timers/animations between tests, so every completion, close and
        rejection path must stop them and schedule cleanup.
        """
        if getattr(self, "_progress_anim", None) is not None:
            self._progress_anim.stop()
            self._progress_anim.deleteLater()
        if getattr(self, "_icon_timer", None) is not None:
            self._icon_timer.stop()
            self._icon_timer.deleteLater()

    def update_progress(self, percent: int, message: str) -> None:
        """Update progress and message.

        Args:
            percent: Progress percentage (0-100).
            message: Status message to display.
        """
        self._progress_bar.setValue(percent)
        self._loading_label.setText(message)

    def set_complete(self) -> None:
        """Stop animations and close dialog."""
        self._stop_animations()
        self.accept()

    def set_error(self, message: str) -> None:
        """Show error message.

        Args:
            message: Error message to display.
        """
        self._loading_label.setText(f"Error: {message}")
        self._progress_bar.setValue(0)

    def set_cancelled(self) -> None:
        """Handle cancellation."""
        self._stop_animations()
        self._loading_label.setText("Operation cancelled")
        self._progress_bar.setValue(0)

    def reject(self) -> None:
        """Stop animations when the dialog is rejected."""
        self._stop_animations()
        super().reject()

    def closeEvent(self, event) -> None:
        """Stop animations on close.

        Args:
            event: Close event.
        """
        self._stop_animations()
        super().closeEvent(event)
