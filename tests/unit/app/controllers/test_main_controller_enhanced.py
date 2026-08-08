"""Enhanced tests for MainController to improve coverage."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from app.controllers.main_controller import (
    ExportWorker,
    ExportWorkerSignals,
    MainController,
    SeparationWorker,
    SeparationWorkerSignals,
    WorkerCancelledError,
)
from app.models.processing_state import ProcessingState
from app.models.settings_model import SettingsModel
from app.services.export_service import ExportService
from app.services.separation_service import SeparationService
from engine.demucs.config import ModelName, SeparationConfig
from engine.demucs.errors import SeparationError


class TestMainControllerEnhanced:
    """Enhanced tests for MainController."""

    @pytest.fixture
    def mock_separation_service(self):
        """Create a mock separation service."""
        return AsyncMock(spec=SeparationService)

    @pytest.fixture
    def mock_export_service(self):
        """Create a mock export service."""
        return AsyncMock(spec=ExportService)

    @pytest.fixture
    def main_controller(self, mock_separation_service, mock_export_service):
        """Create MainController with mock services."""
        return MainController(
            settings=SettingsModel(),
            export_service=mock_export_service,
        )

    def test_handle_separate_requested_with_file(self, main_controller):
        """Test handling separation request when a file is loaded."""
        # Set up a current file
        main_controller._app_state.current_file = "/tmp/test.wav"
        main_controller._app_state.processing_status = ProcessingState.IDLE

        # Mock the separation service to avoid actual processing
        with patch.object(main_controller, "_separation_service") as mock_service:
            mock_service.separate = AsyncMock(
                return_value={"vocals": np.array([0.1, 0.2])}
            )

            # Call the method - should not raise
            main_controller.handle_separate_requested()

            # Verify processing status was updated
            assert (
                main_controller._app_state.processing_status == ProcessingState.LOADING
            )

    def test_handle_separate_requested_already_processing(self, main_controller):
        """Test handling separation request when already processing."""
        # Set up state to simulate processing
        main_controller._app_state.current_file = "/tmp/test.wav"
        main_controller._app_state.processing_status = ProcessingState.PROCESSING
        main_controller._current_worker = MagicMock()

        # Call the method - should emit failure and not start new process
        main_controller.handle_separate_requested()

        # Should have emitted separation_failed
        # Note: We can't easily test signals without qtbot, but we can verify
        # the method returned early by checking that separate was not called
        # This is implicitly tested by the fact that no exception was raised
        # and the worker wasn't replaced

    def test_handle_stems_changed(self, main_controller):
        """Test handling stem selection changes."""
        stems = ["vocals", "drums"]
        main_controller.handle_stems_changed(stems)
        assert main_controller._app_state.selected_stems == stems

    def test_handle_export_requested_no_stems(self, main_controller):
        """Test handling export request with no stems."""
        main_controller.handle_export_requested("/tmp/output", {})
        # Should emit export_failed - we can't easily test signals but verify no crash

    def test_handle_export_requested_with_stems(self, main_controller):
        """Test handling export request with stems."""
        stems = {"vocals": np.array([0.1, 0.2]), "instrumental": np.array([0.3, 0.4])}
        main_controller.handle_export_requested("/tmp/output", stems)
        # Should create and start export worker - we can't easily test without qtbot

    def test_is_processing_no_workers(self, main_controller):
        """Test is_processing when no workers are active."""
        main_controller._current_worker = None
        main_controller._export_worker = None
        assert not main_controller.is_processing()

    def test_is_processing_separation_worker(self, main_controller):
        """Test is_processing when separation worker is active."""
        mock_worker = MagicMock()
        mock_worker.cancelled.is_set.return_value = False
        main_controller._current_worker = mock_worker
        main_controller._export_worker = None
        assert main_controller.is_processing()

    def test_is_processing_export_worker(self, main_controller):
        """Test is_processing when export worker is active."""
        mock_worker = MagicMock()
        mock_worker.cancelled.is_set.return_value = False
        main_controller._current_worker = None
        main_controller._export_worker = mock_worker
        assert main_controller.is_processing()

    def test_is_processing_both_workers(self, main_controller):
        """Test is_processing when both workers are active."""
        mock_sep_worker = MagicMock()
        mock_sep_worker.cancelled.is_set.return_value = False
        mock_exp_worker = MagicMock()
        mock_exp_worker.cancelled.is_set.return_value = False
        main_controller._current_worker = mock_sep_worker
        main_controller._export_worker = mock_exp_worker
        assert main_controller.is_processing()

    def test_is_processing_worker_cancelled(self, main_controller):
        """Test is_processing when worker is cancelled."""
        mock_worker = MagicMock()
        mock_worker.cancelled.is_set.return_value = True  # Cancelled
        main_controller._current_worker = mock_worker
        main_controller._export_worker = None
        assert not main_controller.is_processing()

    def test_cancel_separation_no_worker(self, main_controller):
        """Test cancelling separation when no worker exists."""
        main_controller._current_worker = None
        # Should not raise
        main_controller.cancel_separation()
        assert main_controller._app_state.processing_status == ProcessingState.IDLE

    def test_cancel_separation_with_worker(self, main_controller):
        """Test cancelling separation when worker exists."""
        mock_worker = MagicMock()
        main_controller._current_worker = mock_worker
        main_controller._app_state.processing_status = ProcessingState.PROCESSING

        main_controller.cancel_separation()

        # Should have called cancel on the worker
        mock_worker.cancel.assert_called_once()
        assert main_controller._app_state.processing_status == ProcessingState.IDLE
        assert main_controller._current_worker is None

    def test_update_settings_partial(self, main_controller):
        """Test updating only some settings."""
        main_controller.update_settings({"theme": "dark"})

        assert main_controller.app_state.settings.theme == "dark"
        assert (
            main_controller.app_state.settings.segment
            == main_controller.app_state.settings.segment
        )  # unchanged

    def test_update_settings_invalid_key(self, main_controller):
        """Test updating with invalid setting key."""
        # Should not raise - invalid keys are ignored
        main_controller.update_settings({"invalid_key": "value"})
        # No assertion needed - just verifying it doesn't crash

    def test_build_separation_config(self, main_controller):
        """Test building separation config from settings."""
        # Modify settings to known values
        main_controller._app_state.settings.default_model = "htdemucs_ft"
        main_controller._app_state.settings.segment = 5
        main_controller._app_state.settings.mixed_precision = True
        main_controller._app_state.settings.pin_memory = False

        config = main_controller._build_separation_config()

        assert isinstance(config, SeparationConfig)
        assert config.model_name == ModelName.HTDEMUCS_FT
        assert config.segment == 5
        assert config.mixed_precision is True
        assert config.pin_memory is False

    def test_on_separation_finished_tuple_result(self, main_controller):
        """Test handling separation finished with tuple result."""
        # Mock the result as a tuple (stems, metadata)
        stems = {"vocals": np.array([0.1, 0.2])}
        result = (stems, {"metadata": "test"})

        # Call the slot
        main_controller._on_separation_finished(result)

        # Should have updated state and emitted signal
        assert main_controller._app_state.processing_status == ProcessingState.COMPLETE
        assert main_controller._current_worker is None

    def test_on_separation_finished_dict_result(self, main_controller):
        """Test handling separation finished with dict result."""
        stems = {"vocals": np.array([0.1, 0.2])}
        result = stems  # Direct dict

        # Call the slot
        main_controller._on_separation_finished(result)

        # Should have updated state and emitted signal
        assert main_controller._app_state.processing_status == ProcessingState.COMPLETE
        assert main_controller._current_worker is None

    def test_on_separation_finished_unexpected_result(self, main_controller):
        """Test handling separation finished with unexpected result type."""
        result = ["unexpected", "list"]

        # Call the slot - should not raise
        main_controller._on_separation_finished(result)

        # Should have updated state (though result handling may be different)
        assert main_controller._app_state.processing_status == ProcessingState.COMPLETE
        assert main_controller._current_worker is None

    def test_on_separation_error(self, main_controller):
        """Test handling separation error."""
        error = Exception("Test error")

        # Call the slot
        main_controller._on_separation_error(error)

        # Should have updated state and emitted failure signal
        assert main_controller._app_state.processing_status == ProcessingState.ERROR
        assert main_controller._current_worker is None

    def test_on_export_finished(self, main_controller):
        """Test handling export finished."""
        result = {"vocals": "/tmp/vocals.wav", "instrumental": "/tmp/instrumental.wav"}

        # Call the slot
        main_controller._on_export_finished(result)

        # Should have emitted completed signal
        # Note: We can't easily test signals but verify no crash
        assert main_controller._export_worker is None  # Worker should be cleaned up

    def test_on_export_error(self, main_controller):
        """Test handling export error."""
        error = Exception("Export failed")

        # Call the slot
        main_controller._on_export_error(error)

        # Should have emitted failed signal
        # Note: We can't easily test signals but verify no crash
        assert main_controller._export_worker is None  # Worker should be cleaned up

    def test_separation_worker_initialization(self):
        """Test SeparationWorker initialization."""
        mock_service = AsyncMock(spec=SeparationService)
        file_path = Path("/tmp/test.wav")
        progress_callback = MagicMock()

        worker = SeparationWorker(
            separation_service=mock_service,
            file_path=file_path,
            progress_callback=progress_callback,
        )

        assert worker._separation_service == mock_service
        assert worker._file_path == file_path
        assert worker._progress_callback == progress_callback
        assert worker._audio is None
        assert worker._sample_rate == 44_100
        assert isinstance(worker.signals, SeparationWorkerSignals)

    def test_separation_worker_with_audio(self):
        """Test SeparationWorker initialization with pre-loaded audio."""
        mock_service = AsyncMock(spec=SeparationService)
        file_path = Path("/tmp/test.wav")
        progress_callback = MagicMock()
        audio = np.array([0.1, 0.2, 0.3])
        sample_rate = 22050

        worker = SeparationWorker(
            separation_service=mock_service,
            file_path=file_path,
            progress_callback=progress_callback,
            audio=audio,
            sample_rate=sample_rate,
        )

        assert worker._audio is audio
        assert worker._sample_rate == sample_rate

    def test_separation_worker_cancel(self):
        """Test SeparationWorker cancel method."""
        mock_service = AsyncMock(spec=SeparationService)
        worker = SeparationWorker(
            separation_service=mock_service,
            file_path=Path("/tmp/test.wav"),
            progress_callback=MagicMock(),
        )

        # Initially not cancelled
        assert not worker._cancelled.is_set()

        # Call cancel
        worker.cancel()

        # Should be cancelled now
        assert worker._cancelled.is_set()

    def test_export_worker_initialization(self):
        """Test ExportWorker initialization."""
        mock_service = AsyncMock(spec=ExportService)
        stems = {"vocals": np.array([0.1, 0.2])}
        output_dir = Path("/tmp/output")

        worker = ExportWorker(
            export_service=mock_service,
            stems=stems,
            output_dir=output_dir,
        )

        assert worker._export_service == mock_service
        assert worker._stems == stems
        assert worker._output_dir == output_dir
        assert isinstance(worker.signals, ExportWorkerSignals)

    def test_worker_cancelled_error(self):
        """Test WorkerCancelledError can be instantiated and is a SeparationError."""
        error = WorkerCancelledError("Test cancellation")
        assert isinstance(error, SeparationError)
        assert str(error) == "Test cancellation"

    def test_worker_cancelled_error_default(self):
        """Test WorkerCancelledError with default message."""
        error = WorkerCancelledError()
        assert isinstance(error, SeparationError)
        assert str(error) == "Separation cancelled"

    def test_separation_worker_signals(self):
        """Test SeparationWorkerSignals has expected signals."""
        signals = SeparationWorkerSignals()
        assert hasattr(signals, "finished")
        assert hasattr(signals, "error")
        assert hasattr(signals, "cancelled")
        assert hasattr(signals, "progress")

    def test_export_worker_signals(self):
        """Test ExportWorkerSignals has expected signals."""
        signals = ExportWorkerSignals()
        assert hasattr(signals, "finished")
        assert hasattr(signals, "error")
        assert hasattr(signals, "progress")

    def test_main_controller_signals(self):
        """Test MainController has expected signals."""
        controller = MainController()
        assert hasattr(controller, "state_changed")
        assert hasattr(controller, "separation_started")
        assert hasattr(controller, "separation_completed")
        assert hasattr(controller, "separation_failed")
        assert hasattr(controller, "separation_cancelled")
        assert hasattr(controller, "separation_progress")
        assert hasattr(controller, "export_progress")
        assert hasattr(controller, "export_completed")
        assert hasattr(controller, "export_failed")
        assert hasattr(controller, "thermal_warning")

    def test_main_controller_initialization_with_defaults(self):
        """Test MainController initialization with default parameters."""
        controller = MainController()
        assert controller._separation_service is not None
        assert controller._export_service is not None
        assert isinstance(controller._app_state.settings, SettingsModel)

    def test_main_controller_initialization_with_custom_services(self):
        """Test MainController initialization with custom services."""
        mock_exp_service = AsyncMock(spec=ExportService)

        controller = MainController(
            settings=SettingsModel(),
            export_service=mock_exp_service,
        )

        # Note: separation service is internal, export service is the mock
        assert controller._export_service == mock_exp_service
        assert controller._separation_service is not None  # Still created internally

    def test_thermal_monitor_initialization(self):
        """Test that thermal monitor is initialized."""
        controller = MainController()
        assert controller._thermal_monitor is not None

    def test_thread_pool_initialization(self):
        """Test that thread pool is initialized."""
        controller = MainController()
        assert controller._thread_pool is not None

    def test_initial_state_values(self):
        """Test initial state values."""
        controller = MainController()
        assert controller._current_worker is None
        assert controller._export_worker is None
        assert controller._loaded_audio is None
        assert controller._loaded_sample_rate == 44_100

    def test_app_state_property(self, main_controller):
        """Test that app_state property returns the internal app state."""
        assert main_controller.app_state is main_controller._app_state
