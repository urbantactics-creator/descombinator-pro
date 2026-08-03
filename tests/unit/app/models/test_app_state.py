"""Unit tests for app.models.app_state — AppState."""

from __future__ import annotations

from pathlib import Path

from app.models.app_state import AppState
from app.models.processing_state import ProcessingState


class TestAppStateDefaults:
    def test_default_current_file(self) -> None:
        s = AppState()
        assert s.current_file is None

    def test_default_processing_status(self) -> None:
        s = AppState()
        assert s.processing_status == ProcessingState.IDLE

    def test_default_selected_stems(self) -> None:
        s = AppState()
        assert s.selected_stems == ["vocals", "other"]

    def test_default_settings(self) -> None:
        s = AppState()
        assert s.settings is not None
        assert s.settings.theme == "dark"


class TestAppStateCustom:
    def test_custom_file(self) -> None:
        s = AppState(current_file=Path("/test/audio.wav"))
        assert s.current_file == Path("/test/audio.wav")

    def test_custom_status(self) -> None:
        s = AppState(processing_status=ProcessingState.PROCESSING)
        assert s.processing_status == ProcessingState.PROCESSING

    def test_custom_stems(self) -> None:
        s = AppState(selected_stems=["drums", "bass"])
        assert s.selected_stems == ["drums", "bass"]


class TestAppStateTransitions:
    def test_set_processing(self) -> None:
        s = AppState()
        s.processing_status = ProcessingState.LOADING
        assert s.processing_status == ProcessingState.LOADING
        s.processing_status = ProcessingState.PROCESSING
        assert s.processing_status == ProcessingState.PROCESSING
        s.processing_status = ProcessingState.COMPLETE
        assert s.processing_status == ProcessingState.COMPLETE

    def test_set_error(self) -> None:
        s = AppState()
        s.processing_status = ProcessingState.ERROR
        assert s.processing_status == ProcessingState.ERROR

    def test_set_file(self) -> None:
        s = AppState()
        s.current_file = Path("/new/file.flac")
        assert s.current_file == Path("/new/file.flac")


class TestAppStateSerialization:
    def test_roundtrip(self) -> None:
        s = AppState(
            current_file=Path("/test.wav"),
            processing_status=ProcessingState.COMPLETE,
            selected_stems=["vocals"],
        )
        data = s.model_dump()
        restored = AppState(**data)
        assert restored.current_file == Path("/test.wav")
        assert restored.processing_status == ProcessingState.COMPLETE
        assert restored.selected_stems == ["vocals"]
