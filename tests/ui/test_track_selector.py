"""Tests for the TrackSelector widget."""

from app.widgets.track_selector import TrackSelector


def test_track_selector_creation(qapp):
    """Test that TrackSelector can be created."""
    widget = TrackSelector()
    assert widget is not None
    assert widget.windowTitle() == ""  # No window title for widget


def test_track_selector_default_selection(qapp):
    """Test that TrackSelector has correct default selection."""
    widget = TrackSelector()
    selected = widget.selected_stems
    # Default should be vocals and other
    assert "vocals" in selected
    assert "other" in selected
    assert len(selected) == 2


def test_track_selector_selection_changed(qapp):
    """Test that TrackSelector emits signal when selection changes."""
    widget = TrackSelector()

    # Track the signal emissions
    signals_received = []
    widget.stems_changed.connect(lambda stems: signals_received.append(stems))

    # Change selection - deselect vocals
    checkboxes = widget.findChildren(type(widget._checkboxes["vocals"]))
    for cb in checkboxes:
        if cb.text() == "Vocals":
            cb.setChecked(False)
            break

    # Should have received a signal
    assert len(signals_received) > 0
    # The new selection should not include vocals
    assert "vocals" not in signals_received[0]


def test_track_selector_set_selected_stems(qapp):
    """Test setting selected stems programmatically."""
    widget = TrackSelector()

    # Set to only drums and bass
    widget.set_selected_stems(["drums", "bass"])

    selected = widget.selected_stems
    assert "drums" in selected
    assert "bass" in selected
    assert "vocals" not in selected
    assert "other" not in selected
    assert len(selected) == 2


def test_track_selector_clear_selection(qapp):
    """Test clearing all selections."""
    widget = TrackSelector()

    # Start with default selection
    assert len(widget.selected_stems) > 0

    # Clear selection
    widget.clear_selection()

    # Should have no selections
    assert len(widget.selected_stems) == 0
