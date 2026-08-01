"""Tests for the ProgressBar widget."""

from __future__ import annotations

from app.widgets.progress_bar import ProgressBar


class TestProgressBarInit:
    """Tests for ProgressBar initialization."""

    def test_creates_without_error(self) -> None:
        """ProgressBar can be created."""
        widget = ProgressBar()
        assert widget is not None

    def test_initial_value_is_zero(self) -> None:
        """Initial progress value is 0."""
        widget = ProgressBar()
        assert widget.value == 0

    def test_initial_message_is_ready(self) -> None:
        """Initial message is 'Ready'."""
        widget = ProgressBar()
        assert widget.message == "Ready"


class TestProgressBarProgress:
    """Tests for set_progress."""

    def test_set_progress_updates_value(self) -> None:
        """set_progress updates the bar value."""
        widget = ProgressBar()
        widget.set_progress(50, "Processing...")
        assert widget.value == 50
        assert widget.message == "Processing..."

    def test_set_progress_clamps_to_100(self) -> None:
        """Progress value is clamped to 100."""
        widget = ProgressBar()
        widget.set_progress(150)
        assert widget.value == 100

    def test_set_progress_clamps_to_0(self) -> None:
        """Progress value is clamped to 0."""
        widget = ProgressBar()
        widget.set_progress(-10)
        assert widget.value == 0

    def test_set_progress_message_only(self) -> None:
        """set_progress with message only updates message."""
        widget = ProgressBar()
        widget.set_progress(25, "Loading...")
        assert widget.value == 25
        assert widget.message == "Loading..."


class TestProgressBarReset:
    """Tests for reset."""

    def test_reset(self) -> None:
        """Reset returns to initial state."""
        widget = ProgressBar()
        widget.set_progress(75, "Done")
        widget.reset()
        assert widget.value == 0
        assert widget.message == "Ready"


class TestProgressBarError:
    """Tests for set_error."""

    def test_set_error_shows_message(self) -> None:
        """set_error displays the error message."""
        widget = ProgressBar()
        widget.set_error("Something failed")
        assert widget.value == 0
        assert widget.message == "Something failed"
