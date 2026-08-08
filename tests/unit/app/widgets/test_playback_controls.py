"""Tests for the PlaybackControls widget."""

from app.widgets.playback_controls import PlaybackControls


class TestTimeFormat:
    def test_format_time(self) -> None:
        assert PlaybackControls._format_time(0) == "0:00"
        assert PlaybackControls._format_time(65_000) == "1:05"
        assert PlaybackControls._format_time(3_600_000) == "60:00"
        assert PlaybackControls._format_time(-5) == "0:00"


class TestSeekSlider:
    def test_set_duration_enables_slider_and_label(self, qapp) -> None:
        widget = PlaybackControls()
        widget.set_duration(65_000)
        assert widget._position_slider.isEnabled()
        assert widget._position_slider.maximum() == 65_000
        assert widget._duration_label.text() == "1:05"

    def test_zero_duration_disables_slider(self, qapp) -> None:
        widget = PlaybackControls()
        widget.set_duration(0)
        assert not widget._position_slider.isEnabled()

    def test_set_position_updates_slider_and_label(self, qapp) -> None:
        widget = PlaybackControls()
        widget.set_duration(100_000)
        widget.set_position(65_000)
        assert widget._position_slider.value() == 65_000
        assert widget._position_label.text() == "1:05"

    def test_slider_drag_emits_position_changed(self, qapp) -> None:
        widget = PlaybackControls()
        positions: list[int] = []
        widget.position_changed.connect(positions.append)
        widget.set_duration(100_000)
        widget._on_slider_pressed()
        widget._on_position_slider_moved(5_000)
        assert positions == [5_000]
        widget._position_slider.setValue(7_500)
        widget._on_slider_released()
        assert positions == [5_000, 7_500]
        assert not widget._dragging

    def test_slider_moved_ignored_when_not_dragging(self, qapp) -> None:
        widget = PlaybackControls()
        positions: list[int] = []
        widget.position_changed.connect(positions.append)
        widget.set_duration(100_000)
        widget._on_position_slider_moved(5_000)
        assert positions == []

    def test_set_position_skipped_while_dragging(self, qapp) -> None:
        widget = PlaybackControls()
        widget.set_duration(100_000)
        widget._on_slider_pressed()
        widget.set_position(99_999)
        assert widget._position_slider.value() == 0
        assert widget._position_label.text() == "0:00"
        widget._on_slider_released()


class TestVolume:
    def test_user_change_emits_volume_changed(self, qapp) -> None:
        widget = PlaybackControls()
        volumes: list[float] = []
        widget.volume_changed.connect(volumes.append)
        widget._on_volume_changed(40)
        assert volumes == [0.4]
        assert widget._volume_label.text() == "40%"

    def test_set_volume_is_guarded_against_feedback(self, qapp) -> None:
        widget = PlaybackControls()
        volumes: list[float] = []
        widget.volume_changed.connect(volumes.append)
        widget.set_volume(0.8)
        assert widget._volume_slider.value() == 80
        assert widget._volume_label.text() == "80%"
        assert volumes == []


class TestTransportButtons:
    def test_set_playing_updates_buttons(self, qapp) -> None:
        widget = PlaybackControls()
        widget.set_playing(True)
        assert not widget._play_button.isEnabled()
        assert widget._pause_button.isEnabled()
        widget.set_playing(False)
        assert widget._play_button.isEnabled()
        assert not widget._pause_button.isEnabled()
