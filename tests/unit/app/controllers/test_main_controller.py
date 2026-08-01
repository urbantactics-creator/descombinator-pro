"""Tests for the MainController."""

from __future__ import annotations

from app.controllers.main_controller import MainController
from app.models.processing_state import ProcessingState


class TestMainControllerInit:
    """Tests for MainController initialization."""

    def test_creates_without_error(self) -> None:
        """MainController can be created."""
        ctrl = MainController()
        assert ctrl is not None

    def test_initial_state(self) -> None:
        """Initial state is idle with no file."""
        ctrl = MainController()
        assert ctrl.app_state.processing_status == ProcessingState.IDLE
        assert ctrl.app_state.current_file is None


class TestMainControllerSignals:
    """Tests for signal emissions."""

    def test_handle_file_dropped_updates_state(self) -> None:
        """File drop updates app state."""
        ctrl = MainController()
        ctrl.handle_file_dropped("/tmp/test.wav")
        assert ctrl.app_state.current_file is not None
        assert ctrl.app_state.processing_status == ProcessingState.IDLE

    def test_separate_without_file_fails(self, qapp) -> None:
        """Separation without a file emits failed signal."""
        ctrl = MainController()
        errors = []
        ctrl.separation_failed.connect(lambda msg: errors.append(msg))
        ctrl.handle_separate_requested()
        assert len(errors) == 1
        assert "No file selected" in errors[0]

    def test_separate_while_processing_fails(self, qapp) -> None:
        """Starting separation while already processing emits failed."""
        ctrl = MainController()
        ctrl.handle_file_dropped("/tmp/test.wav")
        ctrl._app_state.processing_status = ProcessingState.PROCESSING
        errors = []
        ctrl.separation_failed.connect(lambda msg: errors.append(msg))
        ctrl.handle_separate_requested()
        assert len(errors) == 1
        assert "Already processing" in errors[0]


class TestMainControllerCancel:
    """Tests for cancel_separation."""

    def test_cancel_resets_state(self) -> None:
        """Cancel resets state to idle."""
        ctrl = MainController()
        ctrl._app_state.processing_status = ProcessingState.PROCESSING
        ctrl.cancel_separation()
        assert ctrl._app_state.processing_status == ProcessingState.IDLE
        assert ctrl._current_worker is None


class TestMainControllerUpdateSettings:
    """Tests for update_settings."""

    def test_update_settings(self) -> None:
        """Updates settings on the app state."""
        ctrl = MainController()
        ctrl.update_settings({"theme": "light"})
        assert ctrl.app_state.settings.theme == "light"
