"""Main controller for coordinating UI and services."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from loguru import logger
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

from app.models.app_state import AppState
from app.models.processing_state import ProcessingState
from app.services.export_service import ExportService
from app.services.separation_service import SeparationService


class SeparationWorkerSignals(QObject):
    """Signals for the separation worker."""

    finished = Signal(object)
    error = Signal(Exception)
    progress = Signal(int, str)


class SeparationWorker(QRunnable):
    """Worker thread for running audio separation."""

    def __init__(
        self,
        separation_service: SeparationService,
        file_path: Path,
        progress_callback: callable,
    ) -> None:
        super().__init__()
        self._separation_service = separation_service
        self._file_path = file_path
        self._progress_callback = progress_callback
        self.signals = SeparationWorkerSignals()
        self._result: dict[str, Any] | None = None
        self._exception: Exception | None = None

    def run(self) -> None:
        """Run the separation process in a separate thread."""
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Run the separation
            result = loop.run_until_complete(
                self._separation_service.separate(
                    self._file_path, progress_callback=self._progress_callback
                )
            )
            self._result = result
            self.signals.finished.emit(self._result)
        except Exception as e:
            self._exception = e
            logger.error(f"Separation failed: {e}")
            self.signals.error.emit(e)
        finally:
            loop.close()


class MainController(QObject):
    """Main controller coordinating UI interactions and services."""

    # Signals for updating the UI
    state_changed = Signal(object)  # AppState
    separation_started = Signal()
    separation_completed = Signal(dict)  # stems dict
    separation_failed = Signal(str)  # error message
    export_completed = Signal(dict)  # stem_name -> file_path
    export_failed = Signal(str)  # error message

    def __init__(self) -> None:
        super().__init__()
        self._app_state = AppState()
        self._separation_service = SeparationService()
        self._export_service = ExportService()
        self._thread_pool = QThreadPool.globalInstance()
        self._current_worker: SeparationWorker | None = None

    @property
    def app_state(self) -> AppState:
        """Get the current application state."""
        return self._app_state

    def initialize_services(self) -> None:
        """Initialize all services."""
        # Initialize separation service
        asyncio.create_task(self._separation_service.initialize())

    def handle_file_dropped(self, file_path: str) -> None:
        """Handle a file being dropped on the UI.

        Args:
            file_path: Path to the dropped file
        """
        path = Path(file_path)
        self._app_state.current_file = path
        self._app_state.processing_status = ProcessingState.IDLE
        self.state_changed.emit(self._app_state)

        # Enable the separate button in the UI
        # This would be handled by the main window connecting to state_changed

    def handle_separate_requested(self) -> None:
        """Handle the user requesting to start separation."""
        if not self._app_state.current_file:
            self.separation_failed.emit("No file selected")
            return

        if self._app_state.processing_status == ProcessingState.PROCESSING:
            self.separation_failed.emit("Already processing")
            return

        # Update state
        self._app_state.processing_status = ProcessingState.LOADING
        self.state_changed.emit(self._app_state)
        self.separation_started.emit()

        # Create and start worker
        def progress_callback(percent: int, message: str) -> None:
            # Emit progress signal
            self.separation_progress.emit(percent, message)

        self._current_worker = SeparationWorker(
            self._separation_service, self._app_state.current_file, progress_callback
        )

        # Connect worker signals
        self._current_worker.signals.finished.connect(self._on_separation_finished)
        self._current_worker.signals.error.connect(self._on_separation_error)
        self._current_worker.signals.progress.connect(
            lambda percent, message: self.separation_progress.emit(percent, message)
        )

        # Start the worker
        self._thread_pool.start(self._current_worker)

    def handle_stems_changed(self, stems: list[str]) -> None:
        """Handle the user changing which stems to process.

        Args:
            stems: List of stem names to process
        """
        self._app_state.selected_stems = stems
        # Note: We don't update processing status here as this is just selection

    def handle_export_requested(self, output_dir: str, stems: dict[str, Any]) -> None:
        """Handle the user requesting to export separated stems.

        Args:
            output_dir: Directory to export to
            stems: Dictionary of separated stems
        """
        if not stems:
            self.export_failed.emit("No processed audio to export")
            return

        # Create export worker
        def export_progress_callback(percent: int, message: str) -> None:
            # For now, we don't have progress reporting in export
            pass

        # Run export in a separate thread to avoid blocking UI
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Run the export
            result = loop.run_until_complete(
                self._export_service.export_stems(stems, Path(output_dir))
            )
            self.export_completed.emit(result)
        except Exception as e:
            logger.error(f"Export failed: {e}")
            self.export_failed.emit(str(e))
        finally:
            loop.close()

    @Slot(object)
    def _on_separation_finished(self, result: dict[str, Any]) -> None:
        """Handle successful separation completion."""
        self._app_state.processing_status = ProcessingState.COMPLETE
        self.state_changed.emit(self._app_state)
        self.separation_completed.emit(result)
        self._current_worker = None

    @Slot(Exception)
    def _on_separation_error(self, error: Exception) -> None:
        """Handle separation error."""
        self._app_state.processing_status = ProcessingState.ERROR
        self.state_changed.emit(self._app_state)
        self.separation_failed.emit(str(error))
        self._current_worker = None

    def cancel_separation(self) -> None:
        """Cancel the ongoing separation process."""
        if self._current_worker:
            # In a real implementation, we'd need to properly cancel the worker
            # For now, we'll just reset the state
            pass
        self._app_state.processing_status = ProcessingState.IDLE
        self.state_changed.emit(self._app_state)
        self._current_worker = None

    def update_settings(self, settings: dict[str, Any]) -> None:
        """Update application settings.

        Args:
            settings: Dictionary of settings to update
        """
        # Update the settings model
        for key, value in settings.items():
            if hasattr(self._app_state.settings, key):
                setattr(self._app_state.settings, key, value)
        self.state_changed.emit(self._app_state)
