"""Main controller for coordinating UI and services."""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
from loguru import logger
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

from app.models.app_state import AppState
from app.models.processing_state import ProcessingState
from app.models.settings_model import SettingsModel
from app.services.export_service import ExportService
from app.services.separation_service import SeparationService
from engine.demucs.config import ModelName, SeparationConfig
from engine.demucs.errors import SeparationError
from engine.performance.thermal import ThermalMonitor


class SeparationWorkerSignals(QObject):
    """Signals for the separation worker."""

    finished = Signal(object)
    error = Signal(Exception)
    cancelled = Signal()
    progress = Signal(int, str)


class WorkerCancelledError(SeparationError):
    """Raised from the progress callback to abort a cancelled separation."""

    def __init__(self, message: str = "Separation cancelled") -> None:
        super().__init__(message)


class SeparationWorker(QRunnable):
    """Worker thread for running audio separation."""

    def __init__(
        self,
        separation_service: SeparationService,
        file_path: Path,
        progress_callback: Callable[[int, str], None],
        audio: np.ndarray | None = None,
        sample_rate: int = 44_100,
    ) -> None:
        """Initialize the separation worker.

        Args:
            separation_service: Service to run separation.
            file_path: Path to the audio file to separate.
            progress_callback: Callback receiving (percent, message).
            audio: Optional pre-decoded audio array.
            sample_rate: Sample rate of the pre-decoded audio.
        """
        super().__init__()
        self._separation_service = separation_service
        self._file_path = file_path
        self._progress_callback = progress_callback
        self._audio = audio
        self._sample_rate = sample_rate
        self.signals = SeparationWorkerSignals()
        self._result: dict[str, Any] | None = None
        self._exception: Exception | None = None
        self._cancelled = threading.Event()

    def cancel(self) -> None:
        """Request cooperative cancellation of this worker."""
        self._cancelled.set()

    def run(self) -> None:
        """Run the separation process in a separate thread."""
        if self._cancelled.is_set():
            self.signals.cancelled.emit()
            return

        def progress(percent: int, message: str) -> None:
            # Cooperative cancellation: abort at the next engine progress tick.
            if self._cancelled.is_set():
                raise WorkerCancelledError()
            self._progress_callback(percent, message)

        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Reuse pre-decoded audio to avoid a second decode when available.
            if self._audio is not None:
                result = loop.run_until_complete(
                    self._separation_service.separate_loaded(
                        self._audio,
                        self._sample_rate,
                        progress_callback=progress,
                    )
                )
            else:
                result = loop.run_until_complete(
                    self._separation_service.separate(
                        self._file_path, progress_callback=progress
                    )
                )
            if self._cancelled.is_set():
                logger.info("Separation cancelled")
                self.signals.cancelled.emit()
            else:
                self._result = result
                self.signals.finished.emit(self._result)
        except Exception as e:
            if self._cancelled.is_set():
                logger.info("Separation cancelled")
                self.signals.cancelled.emit()
            else:
                self._exception = e
                logger.error(f"Separation failed: {e}")
                self.signals.error.emit(e)
        finally:
            loop.close()


class ExportWorkerSignals(QObject):
    """Signals for the export worker."""

    finished = Signal(dict)
    error = Signal(Exception)
    progress = Signal(int, str)


class ExportWorker(QRunnable):
    """Worker thread for exporting stems without blocking the UI (regression A3)."""

    def __init__(
        self,
        export_service: ExportService,
        stems: dict[str, Any],
        output_dir: Path,
        progress_callback: Callable[[int, str], None],
    ) -> None:
        """Initialize the export worker.

        Args:
            export_service: Service to run export.
            stems: Dictionary of separated stems.
            output_dir: Directory to write exported files.
            progress_callback: Callback receiving (percent, message).
        """
        super().__init__()
        self._export_service = export_service
        self._stems = stems
        self._output_dir = output_dir
        self._progress_callback = progress_callback
        self.signals = ExportWorkerSignals()

    def run(self) -> None:
        """Run the export in a separate thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self._export_service.export_stems(
                    self._stems,
                    self._output_dir,
                    progress_callback=self._progress_callback,
                )
            )
            self.signals.finished.emit(result)
        except Exception as e:
            logger.error(f"Export failed: {e}")
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
    separation_cancelled = Signal()
    separation_progress = Signal(int, str)  # percent, message
    export_progress = Signal(int, str)
    export_completed = Signal(dict)  # stem_name -> file_path
    export_failed = Signal(str)  # error message
    thermal_warning = Signal(str, float)  # state, cpu_temp_c

    def __init__(self, settings: SettingsModel | None = None) -> None:
        """Initialize the main controller.

        Args:
            settings: Optional settings model. Uses default SettingsModel if None.
        """
        super().__init__()
        self._app_state = AppState(settings=settings or SettingsModel())
        self._thermal_monitor = ThermalMonitor()
        self._separation_service = SeparationService(
            self._build_separation_config(),
            thermal_monitor=self._thermal_monitor,
        )
        self._export_service = ExportService()
        self._thread_pool = QThreadPool.globalInstance()
        self._current_worker: SeparationWorker | None = None
        self._loaded_audio: np.ndarray | None = None
        self._loaded_sample_rate: int = 44_100

    @property
    def app_state(self) -> AppState:
        """Get the current application state."""
        return self._app_state

    def _build_separation_config(self) -> SeparationConfig:
        """Build a SeparationConfig from the current app settings."""
        settings = self._app_state.settings
        return SeparationConfig(
            model_name=ModelName(str(settings.default_model)),
            segment=settings.segment,
            mixed_precision=settings.mixed_precision,
            pin_memory=settings.pin_memory,
        )

    def handle_file_dropped(self, file_path: str) -> None:
        """Handle a file being dropped on the UI.

        Args:
            file_path: Path to the dropped file
        """
        path = Path(file_path)
        self._app_state.current_file = path
        self._app_state.processing_status = ProcessingState.IDLE
        self._loaded_audio = None
        self.state_changed.emit(self._app_state)

        # Enable the separate button in the UI
        # This would be handled by the main window connecting to state_changed

    def set_loaded_audio(self, audio: np.ndarray, sample_rate: int) -> None:
        """Store audio already decoded for the waveform display.

        ``separate_loaded`` reuses it so a large file is decoded only once.

        Args:
            audio: Decoded audio as float32 numpy array.
            sample_rate: Sample rate of the audio.
        """
        self._loaded_audio = audio
        self._loaded_sample_rate = sample_rate

    def handle_separate_requested(self) -> None:
        """Handle the user requesting to start separation."""
        if not self._app_state.current_file:
            self.separation_failed.emit("No file selected")
            return

        # Guard against concurrent separations. The previous check compared against
        # ProcessingState.PROCESSING, a state never assigned by this controller
        # (only IDLE/LOADING/COMPLETE/ERROR are used), so two quick clicks both
        # passed the guard and launched two SeparationWorkers sharing the same
        # non-reentrant SeparationService/separator and ResourceMonitor.
        if self._current_worker is not None or self._app_state.processing_status in (
            ProcessingState.LOADING,
            ProcessingState.PROCESSING,
            ProcessingState.CANCELLED,
        ):
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
            self._separation_service,
            self._app_state.current_file,
            progress_callback,
            audio=self._loaded_audio,
            sample_rate=self._loaded_sample_rate,
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

        # Rebuild the separation service so new engine settings take effect.
        # Skip while a worker is running: it holds a reference to the old service.
        if self._current_worker is None:
            self._separation_service = SeparationService(
                self._build_separation_config()
            )
        self.state_changed.emit(self._app_state)
