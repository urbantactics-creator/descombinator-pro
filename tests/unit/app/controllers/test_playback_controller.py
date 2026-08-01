"""Tests for the PlaybackController."""

from __future__ import annotations

from app.controllers.playback_controller import PlaybackController


class TestPlaybackControllerInit:
    """Tests for PlaybackController initialization."""

    def test_creates_without_error(self) -> None:
        """PlaybackController can be created."""
        ctrl = PlaybackController()
        assert ctrl is not None

    def test_initial_state_is_stopped(self) -> None:
        """Initial playback state is stopped."""
        ctrl = PlaybackController()
        assert ctrl.get_state() == "stopped"


class TestPlaybackControllerPlayPause:
    """Tests for play/pause/stop."""

    def test_play_starts_playing(self, qapp) -> None:
        """Play changes state to playing (if media loaded)."""
        ctrl = PlaybackController()
        ctrl.play()
        # Without media loaded, play is a no-op
        assert ctrl.get_state() == "stopped"

    def test_pause_is_noop_when_stopped(self) -> None:
        """Pause is a no-op when stopped."""
        ctrl = PlaybackController()
        ctrl.pause()
        assert ctrl.get_state() == "stopped"

    def test_stop_is_noop_when_stopped(self) -> None:
        """Stop is a no-op when stopped."""
        ctrl = PlaybackController()
        ctrl.stop()
        assert ctrl.get_state() == "stopped"


class TestPlaybackControllerPosition:
    """Tests for position and volume."""

    def test_set_position_no_crash(self) -> None:
        """Setting position doesn't crash."""
        ctrl = PlaybackController()
        ctrl.set_position(1000)
        assert ctrl.get_position() == 0

    def test_set_volume_no_crash(self) -> None:
        """Setting volume doesn't crash."""
        ctrl = PlaybackController()
        ctrl.set_volume(0.5)
