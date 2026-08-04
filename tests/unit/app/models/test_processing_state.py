"""Unit tests for app.models.processing_state — ProcessingState."""

from __future__ import annotations

from app.models.processing_state import ProcessingState


class TestProcessingStateMembers:
    """Tests for ProcessingState StrEnum members."""

    def test_idle_exists(self) -> None:
        assert ProcessingState.IDLE is not None

    def test_loading_exists(self) -> None:
        assert ProcessingState.LOADING is not None

    def test_processing_exists(self) -> None:
        assert ProcessingState.PROCESSING is not None

    def test_complete_exists(self) -> None:
        assert ProcessingState.COMPLETE is not None

    def test_error_exists(self) -> None:
        assert ProcessingState.ERROR is not None

    def test_cancelled_exists(self) -> None:
        assert ProcessingState.CANCELLED is not None


class TestProcessingStateValues:
    """Tests for string values of ProcessingState."""

    def test_idle_value(self) -> None:
        assert ProcessingState.IDLE == "idle"

    def test_loading_value(self) -> None:
        assert ProcessingState.LOADING == "loading"

    def test_processing_value(self) -> None:
        assert ProcessingState.PROCESSING == "processing"

    def test_complete_value(self) -> None:
        assert ProcessingState.COMPLETE == "complete"

    def test_error_value(self) -> None:
        assert ProcessingState.ERROR == "error"

    def test_cancelled_value(self) -> None:
        assert ProcessingState.CANCELLED == "cancelled"


class TestProcessingStateEnumBehavior:
    """Tests for enum iteration and comparison."""

    def test_iteration_yields_all_members(self) -> None:
        members = list(ProcessingState)
        assert len(members) == 6

    def test_string_comparison(self) -> None:
        assert ProcessingState.IDLE == "idle"
        assert ProcessingState.PROCESSING == "processing"
        assert ProcessingState.CANCELLED == "cancelled"

    def test_membership_by_value(self) -> None:
        values = [e.value for e in ProcessingState]
        assert "idle" in values
        assert "loading" in values
        assert "processing" in values
        assert "complete" in values
        assert "error" in values
        assert "cancelled" in values

    def test_all_values_are_strings(self) -> None:
        for member in ProcessingState:
            assert isinstance(member.value, str)
