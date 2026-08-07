"""Tests for the MainController."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np

from app.controllers.main_controller import MainController
from app.models.processing_state import ProcessingState
from engine.demucs.config import SeparationConfig


class TestMainControllerLoadedAudio:
    """Tests for set_loaded_audio and pre-loaded separation."""

    def test_set_loaded_audio_stores_values(self) -> None:
        """Decoded audio and its sample rate are stored."""
        ctrl = MainController()
        audio = np.zeros(44100, dtype=np.float32)

        ctrl.set_loaded_audio(audio, 44100)

        assert ctrl._loaded_audio is audio
        assert ctrl._loaded_sample_rate == 44100

    def test_handle_file_dropped_resets_loaded_audio(self) -> None:
        """A new file drop clears the previously loaded audio."""
        ctrl = MainController()
        ctrl.set_loaded_audio(np.zeros(44100, dtype=np.float32), 44100)

        ctrl.handle_file_dropped("/tmp/new.wav")

        assert ctrl._loaded_audio is None

    def test_worker_uses_separate_loaded_when_audio_present(self) -> None:
        """Pre-loaded audio routes to separate_loaded (single decode)."""
        ctrl = MainController()
        ctrl.handle_file_dropped("/tmp/song.wav")
        audio = np.zeros(44100, dtype=np.float32)
        ctrl.set_loaded_audio(audio, 44100)

        mock_service = MagicMock()
        mock_service.separate_loaded = AsyncMock(
            return_value=(
                {"vocals": np.zeros(44100, dtype=np.float32)},
                44100,
            )
        )
        with patch.object(ctrl, "_separation_service", mock_service):
            ctrl.handle_separate_requested()

        worker = ctrl._current_worker
        assert worker is not None
        assert worker._audio is audio
        assert worker._sample_rate == 44100


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

    def test_separate_while_loading_fails(self, qapp) -> None:
        """A second click while LOADING is rejected (regression for C3)."""
        ctrl = MainController()
        ctrl.handle_file_dropped("/tmp/test.wav")
        ctrl._app_state.processing_status = ProcessingState.LOADING
        errors = []
        ctrl.separation_failed.connect(lambda msg: errors.append(msg))
        ctrl.handle_separate_requested()
        assert len(errors) == 1
        assert "Already processing" in errors[0]

    def test_separate_with_active_worker_fails(self, qapp) -> None:
        """A second click while a worker is alive is rejected (regression for C3)."""
        ctrl = MainController()
        ctrl.handle_file_dropped("/tmp/test.wav")
        ctrl._current_worker = object()  # type: ignore[assignment]
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


class TestMainControllerBuildSeparationConfig:
    """Tests for _build_separation_config."""

    def test_build_defaults(self) -> None:
        """Default settings build a default SeparationConfig."""
        ctrl = MainController()
        cfg = ctrl._build_separation_config()
        assert isinstance(cfg, SeparationConfig)
        assert cfg.segment is None
        assert cfg.mixed_precision is False
        assert cfg.pin_memory is False
        assert cfg.model_name.value == "htdemucs_ft"

    def test_build_maps_settings(self) -> None:
        """Advanced settings flow into SeparationConfig."""
        ctrl = MainController()
        ctrl.app_state.settings.segment = 8
        ctrl.app_state.settings.mixed_precision = True
        ctrl.app_state.settings.pin_memory = True
        ctrl.app_state.settings.default_model = "umxhq"

        cfg = ctrl._build_separation_config()
        assert cfg.segment == 8
        assert cfg.mixed_precision is True
        assert cfg.pin_memory is True
        assert cfg.model_name.value == "umxhq"

    def test_update_settings_rebuilds_service(self) -> None:
        """update_settings rebuilds the separation service with new config."""
        ctrl = MainController()
        old_service = ctrl._separation_service

        ctrl.update_settings(
            {"segment": 12, "mixed_precision": True, "pin_memory": True}
        )

        assert ctrl._separation_service is not old_service
        cfg = ctrl._separation_service._config
        assert isinstance(cfg, SeparationConfig)
        assert cfg.segment == 12
        assert cfg.mixed_precision is True
        assert cfg.pin_memory is True

    def test_update_settings_keeps_service_while_processing(self) -> None:
        """A running worker keeps the old service reference."""
        ctrl = MainController()
        old_service = ctrl._separation_service
        with patch.object(ctrl, "_current_worker", object()):
            ctrl.update_settings({"segment": 20})

        assert ctrl._separation_service is old_service
