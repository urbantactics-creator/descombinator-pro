"""Tests for the widgets."""

from app.widgets.file_drop_zone import FileDropZone
from app.widgets.playback_controls import PlaybackControls
from app.widgets.progress_bar import ProgressBar
from app.widgets.track_selector import TrackSelector
from app.widgets.waveform_view import WaveformView


def test_file_drop_zone_creation(qapp):
    """Test that FileDropZone can be created."""
    widget = FileDropZone()
    assert widget is not None


def test_playback_controls_creation(qapp):
    """Test that PlaybackControls can be created."""
    widget = PlaybackControls()
    assert widget is not None


def test_progress_bar_creation(qapp):
    """Test that ProgressBar can be created."""
    widget = ProgressBar()
    assert widget is not None


def test_track_selector_creation(qapp):
    """Test that TrackSelector can be created."""
    widget = TrackSelector()
    assert widget is not None


def test_waveform_view_creation(qapp):
    """Test that WaveformView can be created."""
    widget = WaveformView()
    assert widget is not None
