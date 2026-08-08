"""Tests for the TrackMixerWidget."""

from app.widgets.track_mixer import TrackMixerWidget


class TestTrackManagement:
    def test_set_tracks_builds_rows(self, qapp) -> None:
        widget = TrackMixerWidget()
        widget.set_tracks(["vocals", "bass"], {"vocals": 0.5}, {"bass": True})
        assert widget.track_names() == ["vocals", "bass"]
        assert widget.is_muted("bass")
        assert not widget.is_muted("vocals")
        assert widget.isEnabled()

    def test_set_tracks_empty_disables(self, qapp) -> None:
        widget = TrackMixerWidget()
        widget.set_tracks(["vocals"])
        widget.set_tracks([])
        assert not widget.isEnabled()
        assert widget.track_names() == []

    def test_add_remove_clear(self, qapp) -> None:
        widget = TrackMixerWidget()
        widget.add_track("a")
        widget.add_track("b")
        assert widget.track_names() == ["a", "b"]
        widget.remove_track("a")
        assert widget.track_names() == ["b"]
        widget.clear()
        assert widget.track_names() == []

    def test_remove_track_preserves_remaining_state(self, qapp) -> None:
        widget = TrackMixerWidget()
        widget.add_track("a", volume=0.4, muted=True)
        widget.add_track("b", volume=0.9, muted=False)
        widget.remove_track("a")
        assert widget._rows["b"][0].value() == 90
        assert not widget.is_muted("b")


class TestSignals:
    def test_slider_value_changed_emits_volume_changed(self, qapp) -> None:
        widget = TrackMixerWidget()
        widget.add_track("vocals")
        volumes: list[tuple[str, float]] = []
        widget.volume_changed.connect(lambda n, v: volumes.append((n, v)))
        widget._rows["vocals"][0].setValue(50)
        assert volumes == [("vocals", 0.5)]

    def test_mute_click_emits_muted_changed(self, qapp) -> None:
        widget = TrackMixerWidget()
        widget.set_tracks(["vocals"])
        muted: list[tuple[str, bool]] = []
        widget.muted_changed.connect(lambda n, m: muted.append((n, m)))
        button = widget._rows["vocals"][1]
        button.click()
        assert muted == [("vocals", True)]
        assert widget.is_muted("vocals")
        assert button.text() == "Muted"

    def test_programmatic_updates_are_guarded(self, qapp) -> None:
        widget = TrackMixerWidget()
        widget.add_track("vocals")
        volumes: list[tuple[str, float]] = []
        muted: list[tuple[str, bool]] = []
        widget.volume_changed.connect(lambda n, v: volumes.append((n, v)))
        widget.muted_changed.connect(lambda n, m: muted.append((n, m)))
        widget.set_track_volume("vocals", 0.3)
        widget.set_track_muted("vocals", True)
        assert widget._rows["vocals"][0].value() == 30
        assert widget.is_muted("vocals")
        assert widget._rows["vocals"][1].text() == "Muted"
        assert volumes == []
        assert muted == []
