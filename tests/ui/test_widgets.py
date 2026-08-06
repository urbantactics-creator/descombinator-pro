"""Behavioral tests for the custom widgets."""

import numpy as np

from app.widgets.file_drop_zone import FileDropZone
from app.widgets.playback_controls import PlaybackControls
from app.widgets.progress_bar import ProgressBar
from app.widgets.track_mixer import TrackMixerWidget
from app.widgets.track_selector import TrackSelector
from app.widgets.waveform_view import WaveformView, decimate_waveform


def test_file_drop_zone_creation(qapp):
    """Test that FileDropZone can be created."""
    widget = FileDropZone()
    assert widget is not None


def test_file_drop_zone_set_message(qapp):
    """Test setting a custom message on the FileDropZone."""
    widget = FileDropZone()
    widget.set_message("Custom message")
    assert "Custom message" in widget._label.text()


def test_playback_controls_creation(qapp):
    """Test that PlaybackControls can be created."""
    widget = PlaybackControls()
    assert widget is not None


def test_playback_controls_signals(qapp):
    """Test that play/pause/stop buttons emit their signals."""
    widget = PlaybackControls()

    play_calls = []
    pause_calls = []
    stop_calls = []

    widget.play_clicked.connect(lambda: play_calls.append(1))
    widget.pause_clicked.connect(lambda: pause_calls.append(1))
    widget.stop_clicked.connect(lambda: stop_calls.append(1))

    widget._on_play_clicked()
    widget._on_pause_clicked()
    widget._on_stop_clicked()

    assert len(play_calls) == 1
    assert len(pause_calls) == 1
    assert len(stop_calls) == 1


def test_playback_controls_set_playing(qapp):
    """Test set_playing updates button enabled state."""
    widget = PlaybackControls()
    widget.set_playing(True)
    assert not widget._play_button.isEnabled()
    assert widget._pause_button.isEnabled()

    widget.set_playing(False)
    assert widget._play_button.isEnabled()
    assert not widget._pause_button.isEnabled()


def test_playback_controls_set_duration(qapp):
    """Test set_duration updates slider range and label."""
    widget = PlaybackControls()
    widget.set_duration(90_000)
    assert widget._duration_ms == 90_000
    assert widget._position_slider.maximum() == 90_000
    assert widget._duration_label.text() == "1:30"
    assert widget._position_slider.isEnabled()


def test_playback_controls_set_position(qapp):
    """Test set_position updates slider and time label."""
    widget = PlaybackControls()
    widget.set_duration(60_000)
    widget.set_position(30_000)
    assert widget._position_slider.value() == 30_000
    assert widget._position_label.text() == "0:30"


def test_playback_controls_set_volume(qapp):
    """Test set_volume updates slider without emitting a signal."""
    widget = PlaybackControls()
    emitted = []
    widget.volume_changed.connect(lambda v: emitted.append(v))
    widget.set_volume(0.5)
    assert widget._volume_slider.value() == 50
    assert widget._volume_label.text() == "50%"
    assert emitted == []


def test_playback_controls_volume_slider_emits(qapp):
    """Test that dragging the volume slider emits volume_changed."""
    widget = PlaybackControls()
    emitted = []
    widget.volume_changed.connect(lambda v: emitted.append(v))
    widget._volume_slider.setValue(80)
    assert emitted == [0.8]
    assert widget._volume_label.text() == "80%"


def test_playback_controls_seek_drag(qapp):
    """Test live seek dragging emits position_changed."""
    widget = PlaybackControls()
    widget.set_duration(60_000)
    emitted = []
    widget.position_changed.connect(lambda pos: emitted.append(pos))

    widget._on_slider_pressed()
    widget._position_slider.setValue(10_000)
    widget._on_position_slider_moved(10_000)
    assert emitted == [10_000]
    assert widget._position_label.text() == "0:10"

    widget._on_slider_released()
    assert emitted == [10_000, 10_000]


def test_playback_controls_format_time(qapp):
    """Test the m:ss time formatting."""
    assert PlaybackControls._format_time(0) == "0:00"
    assert PlaybackControls._format_time(59_000) == "0:59"
    assert PlaybackControls._format_time(60_000) == "1:00"
    assert PlaybackControls._format_time(90_000) == "1:30"
    assert PlaybackControls._format_time(-5) == "0:00"


def test_progress_bar_creation(qapp):
    """Test that ProgressBar can be created."""
    widget = ProgressBar()
    assert widget is not None


def test_progress_bar_set_progress(qapp):
    """Test set_progress updates value and message."""
    widget = ProgressBar()
    widget.set_progress(50, "Processing...")
    assert widget.value == 50
    assert widget.message == "Processing..."
    assert widget._bar.value() == 50


def test_progress_bar_clamps(qapp):
    """Test that set_progress clamps values to 0-100."""
    widget = ProgressBar()
    widget.set_progress(150)
    assert widget.value == 100
    widget.set_progress(-10)
    assert widget.value == 0


def test_progress_bar_reset(qapp):
    """Test reset restores initial state."""
    widget = ProgressBar()
    widget.set_progress(80, "Working")
    widget.set_error("Something failed")
    widget.reset()
    assert widget.value == 0
    assert widget.message == "Ready"


def test_progress_bar_set_error(qapp):
    """Test set_error displays the error state."""
    widget = ProgressBar()
    widget.set_error("Boom")
    assert widget.value == 0
    assert widget.message == "Boom"
    assert "Error: Boom" in widget._bar.format()


def test_track_selector_creation(qapp):
    """Test that TrackSelector can be created."""
    widget = TrackSelector()
    assert widget is not None
    assert widget.selected_stems == ["vocals", "other"]


def test_track_selector_stems_changed(qapp):
    """Test stems_changed signal is emitted on checkbox toggle."""
    widget = TrackSelector()
    emitted = []
    widget.stems_changed.connect(lambda stems: emitted.append(stems))

    widget._checkboxes["drums"].setChecked(True)
    assert emitted and emitted[-1] == ["vocals", "drums", "other"]


def test_track_selector_set_selected_stems(qapp):
    """Test set_selected_stems updates the checkboxes."""
    widget = TrackSelector()
    widget.set_selected_stems(["bass", "drums"])
    assert widget.selected_stems == ["drums", "bass"]


def test_track_selector_clear_selection(qapp):
    """Test clear_selection unchecks all stems."""
    widget = TrackSelector()
    widget.clear_selection()
    assert widget.selected_stems == []


def test_track_mixer_creation(qapp):
    """Test that TrackMixerWidget can be created."""
    widget = TrackMixerWidget()
    assert widget is not None
    assert not widget.isEnabled()


def test_track_mixer_set_tracks(qapp):
    """Test set_tracks builds rows and enables the widget."""
    widget = TrackMixerWidget()
    widget.set_tracks(["vocals", "drums"], {"vocals": 0.8}, {"drums": True})
    assert widget.track_names() == ["vocals", "drums"]
    assert widget.isEnabled()
    assert widget.is_muted("drums")
    assert widget._rows["vocals"][0].value() == 80


def test_track_mixer_volume_changed_signal(qapp):
    """Test volume slider changes emit volume_changed."""
    widget = TrackMixerWidget()
    widget.set_tracks(["vocals"])
    emitted = []
    widget.volume_changed.connect(lambda name, vol: emitted.append((name, vol)))
    widget._rows["vocals"][0].setValue(60)
    assert emitted == [("vocals", 0.6)]


def test_track_mixer_mute_toggle(qapp):
    """Test mute button toggles muted_changed signal and button text."""
    widget = TrackMixerWidget()
    widget.set_tracks(["vocals"])
    emitted = []
    widget.muted_changed.connect(lambda name, muted: emitted.append((name, muted)))
    widget._rows["vocals"][1].click()
    assert emitted == [("vocals", True)]
    assert widget.is_muted("vocals")
    assert widget._rows["vocals"][1].text() == "Muted"


def test_track_mixer_set_volume_programmatic(qapp):
    """Test programmatic volume updates do not emit signals."""
    widget = TrackMixerWidget()
    widget.set_tracks(["vocals"])
    emitted = []
    widget.volume_changed.connect(lambda name, vol: emitted.append((name, vol)))
    widget.set_track_volume("vocals", 0.4)
    assert widget._rows["vocals"][0].value() == 40
    assert emitted == []


def test_track_mixer_remove_track(qapp):
    """Test remove_track preserves remaining rows."""
    widget = TrackMixerWidget()
    widget.set_tracks(["vocals", "drums"])
    widget.remove_track("drums")
    assert widget.track_names() == ["vocals"]
    assert widget.isEnabled()


def test_track_mixer_clear(qapp):
    """Test clear removes all rows."""
    widget = TrackMixerWidget()
    widget.set_tracks(["vocals"])
    widget.clear()
    assert widget.track_names() == []


def test_waveform_view_creation(qapp):
    """Test that WaveformView can be created."""
    widget = WaveformView()
    assert widget is not None


def test_waveform_view_set_audio_data(qapp):
    """Test set_audio_data renders a waveform."""
    widget = WaveformView()
    audio = np.sin(np.linspace(0, 200, 44100)).astype(np.float32)
    widget.set_audio_data(audio, 44100)
    assert widget._audio_data is not None
    assert widget._position_line.isVisible()


def test_waveform_view_set_position(qapp):
    """Test set_position moves the position indicator."""
    widget = WaveformView()
    widget.set_position(1.5)
    assert widget._position_line.value() == 1.5


def test_waveform_view_clear(qapp):
    """Test clear resets the waveform."""
    widget = WaveformView()
    audio = np.zeros(44100, dtype=np.float32)
    widget.set_audio_data(audio, 44100)
    widget.clear()
    assert widget._audio_data is None
    assert not widget._position_line.isVisible()


def test_decimate_waveform_mono(qapp):
    """Test decimate_waveform on mono audio."""
    audio = np.sin(np.linspace(0, 100, 44100)).astype(np.float32)
    points, time_step = decimate_waveform(audio, max_points=1000, sample_rate=44100)
    assert len(points) > 0
    assert len(points) <= 44100
    assert time_step > 0


def test_decimate_waveform_stereo(qapp):
    """Test decimate_waveform on stereo audio."""
    audio = np.zeros((2, 44100), dtype=np.float32)
    points, time_step = decimate_waveform(audio, max_points=500, sample_rate=44100)
    assert len(points) > 0
    assert len(points) <= 44100


def test_decimate_waveform_empty(qapp):
    """Test decimate_waveform on empty audio."""
    points, time_step = decimate_waveform(np.array([], dtype=np.float32))
    assert len(points) == 0
    assert time_step > 0
