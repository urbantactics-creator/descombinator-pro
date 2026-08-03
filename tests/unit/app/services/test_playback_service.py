"""Unit tests for app.services.playback_service — PlaybackService with mock mixer."""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np

from app.audio.mixer import PlaybackState
from app.services.playback_service import PlaybackService


def _make_svc() -> tuple[PlaybackService, MagicMock]:
    mixer = MagicMock()
    mixer.state = PlaybackState.STOPPED
    mixer.position_ms.return_value = 0
    mixer.duration_ms.return_value = 0
    mixer.has_tracks = False
    mixer.track_names.return_value = []
    mixer.track_gains.return_value = {}
    mixer.track_muted_map.return_value = {}
    mixer.active_stems.return_value = []
    svc = PlaybackService(mixer=mixer)
    return svc, mixer


class TestPlaybackServiceInit:
    def test_creates_with_mock_mixer(self) -> None:
        svc, mixer = _make_svc()
        assert svc._mixer is mixer

    def test_creates_without_mixer(self) -> None:
        svc = PlaybackService()
        assert svc._mixer is not None


class TestPlaybackServiceSetSource:
    def test_set_source_calls_mixer(self) -> None:
        svc, mixer = _make_svc()
        audio = np.zeros(44100, dtype=np.float32)
        svc.set_source(audio, 44100)
        mixer.set_tracks.assert_called_once()

    def test_set_source_stereo_to_mono(self) -> None:
        svc, mixer = _make_svc()
        stereo = np.zeros((2, 44100), dtype=np.float32)
        svc.set_source(stereo, 44100)
        mixer.set_tracks.assert_called_once()
        track = mixer.set_tracks.call_args[0][0][0]
        assert track.name == "source"
        assert track.data.ndim == 1


class TestPlaybackServiceSetStems:
    def test_set_stems_delegates_to_mixer(self) -> None:
        svc, mixer = _make_svc()
        stems = {
            "vocals": np.zeros(44100, dtype=np.float32),
            "drums": np.zeros(44100, dtype=np.float32),
        }
        svc.set_stems(stems, 44100)
        mixer.set_tracks.assert_called_once()
        args = mixer.set_tracks.call_args[0][0]
        assert len(args) == 2
        names = [t.name for t in args]
        assert "vocals" in names
        assert "drums" in names


class TestPlaybackServiceClear:
    def test_clear_resets_mixer(self) -> None:
        svc, mixer = _make_svc()
        svc.clear()
        mixer.set_tracks.assert_called_once_with([])


class TestPlaybackServicePlayPauseStop:
    def test_play(self) -> None:
        svc, mixer = _make_svc()
        svc.play()
        mixer.play.assert_called_once()

    def test_pause(self) -> None:
        svc, mixer = _make_svc()
        svc.pause()
        mixer.pause.assert_called_once()

    def test_stop(self) -> None:
        svc, mixer = _make_svc()
        svc.stop()
        mixer.stop.assert_called_once()


class TestPlaybackServiceSeek:
    def test_seek_ms(self) -> None:
        svc, mixer = _make_svc()
        svc.seek_ms(1000)
        mixer.seek_ms.assert_called_once_with(1000)

    def test_set_position_alias(self) -> None:
        svc, mixer = _make_svc()
        svc.set_position(500)
        mixer.seek_ms.assert_called_once_with(500)


class TestPlaybackServiceVolume:
    def test_set_master_volume(self) -> None:
        svc, mixer = _make_svc()
        svc.set_master_volume(0.75)
        mixer.set_master_volume.assert_called_once_with(0.75)

    def test_set_volume_alias(self) -> None:
        svc, mixer = _make_svc()
        svc.set_volume(0.5)
        mixer.set_master_volume.assert_called_once_with(0.5)

    def test_set_track_volume(self) -> None:
        svc, mixer = _make_svc()
        svc.set_track_volume("vocals", 0.8)
        mixer.set_track_gain.assert_called_once_with("vocals", 0.8)


class TestPlaybackServiceMute:
    def test_set_track_muted(self) -> None:
        svc, mixer = _make_svc()
        svc.set_track_muted("vocals", True)
        mixer.set_track_muted.assert_called_once_with("vocals", True)


class TestPlaybackServiceActiveStems:
    def test_set_active_stems(self) -> None:
        svc, mixer = _make_svc()
        svc.set_active_stems(["vocals", "drums"])
        mixer.set_active.assert_called_once_with(["vocals", "drums"])


class TestPlaybackServiceGetters:
    def test_get_state(self) -> None:
        svc, mixer = _make_svc()
        mixer.state = PlaybackState.PLAYING
        assert svc.get_state() == PlaybackState.PLAYING

    def test_get_position(self) -> None:
        svc, mixer = _make_svc()
        mixer.position_ms.return_value = 1500
        assert svc.get_position() == 1500

    def test_get_duration(self) -> None:
        svc, mixer = _make_svc()
        mixer.duration_ms.return_value = 30000
        assert svc.get_duration() == 30000

    def test_has_tracks(self) -> None:
        svc, mixer = _make_svc()
        mixer.has_tracks = True
        assert svc.has_tracks() is True

    def test_track_names(self) -> None:
        svc, mixer = _make_svc()
        mixer.track_names.return_value = ["vocals", "drums"]
        assert svc.track_names() == ["vocals", "drums"]

    def test_track_volumes(self) -> None:
        svc, mixer = _make_svc()
        mixer.track_gains.return_value = {"vocals": 0.8}
        assert svc.track_volumes() == {"vocals": 0.8}

    def test_muted_map(self) -> None:
        svc, mixer = _make_svc()
        mixer.track_muted_map.return_value = {"vocals": True}
        assert svc.muted_map() == {"vocals": True}

    def test_active_stems(self) -> None:
        svc, mixer = _make_svc()
        mixer.active_stems.return_value = ["vocals"]
        assert svc.active_stems() == ["vocals"]


class TestPlaybackServiceHasStems:
    def test_has_stems_false_when_empty(self) -> None:
        svc, mixer = _make_svc()
        mixer.track_names.return_value = []
        assert svc.has_stems() is False

    def test_has_stems_false_when_only_source(self) -> None:
        svc, mixer = _make_svc()
        mixer.track_names.return_value = ["source"]
        assert svc.has_stems() is False

    def test_has_stems_true_when_separated(self) -> None:
        svc, mixer = _make_svc()
        mixer.track_names.return_value = ["vocals", "drums"]
        assert svc.has_stems() is True


class TestPlaybackServiceAsMono:
    def test_mono_passthrough(self) -> None:
        mono = np.zeros(100, dtype=np.float32)
        result = PlaybackService._as_mono(mono)
        assert result.ndim == 1

    def test_stereo_to_mono(self) -> None:
        stereo = np.zeros((2, 100), dtype=np.float32)
        result = PlaybackService._as_mono(stereo)
        assert result.ndim == 1
        assert len(result) == 100

    def test_preserves_float32(self) -> None:
        audio = np.zeros(100, dtype=np.float64)
        result = PlaybackService._as_mono(audio)
        assert result.dtype == np.float32


class TestPlaybackServiceSignalForwarding:
    def test_mixer_signals_connected(self) -> None:
        svc, mixer = _make_svc()
        assert mixer.state_changed.connect.called
        assert mixer.position_changed.connect.called
        assert mixer.duration_changed.connect.called
        assert mixer.error_occurred.connect.called
