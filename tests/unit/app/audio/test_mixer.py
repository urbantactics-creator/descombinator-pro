"""Unit tests for AudioMixer and MixerTrack."""

import numpy as np

from app.audio.mixer import AudioMixer, MixerTrack, PlaybackState


class FakeSink:
    """Fake QAudioSink recording calls for tests."""

    def __init__(self) -> None:
        self.started = 0
        self.stopped = 0
        self.reset_count = 0
        self.suspended = 0
        self.resumed = 0
        self.volume: float | None = None

    def start(self, device: object) -> None:
        self.started += 1

    def stop(self) -> None:
        self.stopped += 1

    def reset(self) -> None:
        self.reset_count += 1

    def suspend(self) -> None:
        self.suspended += 1

    def resume(self) -> None:
        self.resumed += 1

    def setVolume(self, volume: float) -> None:
        self.volume = volume


def _decode(data: bytes) -> np.ndarray:
    """Decode float32 interleaved stereo output."""
    return np.frombuffer(data, dtype=np.float32).reshape(-1, 2)


def _mixer_with_playback_sink() -> tuple[AudioMixer, FakeSink]:
    """Mixer ready to play using a fake sink."""
    mixer = AudioMixer(sink_factory=lambda fmt: FakeSink())
    mixer.set_tracks([MixerTrack("a", np.ones(44100, dtype=np.float32), 44100)])
    mixer._sink = mixer._sink_factory(None)
    mixer._ensure_sink = lambda: True  # type: ignore[method-assign]
    return mixer, mixer._sink


class TestReadData:
    """Tests for the readData mixing logic."""

    def test_mixes_two_tracks_interleaved_mono_to_stereo(self) -> None:
        mixer = AudioMixer()
        mixer.set_tracks(
            [
                MixerTrack("a", np.full(1000, 0.1, dtype=np.float32), 44100),
                MixerTrack("b", np.full(1000, 0.2, dtype=np.float32), 44100),
            ]
        )
        out = _decode(mixer.readData(1000 * 8))
        assert out.shape == (1000, 2)
        np.testing.assert_allclose(out, 0.3, atol=1e-6)

    def test_zero_maxlen_returns_empty(self) -> None:
        mixer = AudioMixer()
        assert mixer.readData(0) == b""

    def test_short_chunk_pads_with_silence(self) -> None:
        mixer = AudioMixer()
        mixer.set_tracks([MixerTrack("a", np.ones(10, dtype=np.float32), 44100)])
        out = _decode(mixer.readData(100 * 8))
        np.testing.assert_allclose(out[:10], 1.0, atol=1e-6)
        np.testing.assert_allclose(out[10:], 0.0, atol=1e-6)

    def test_track_gain_is_applied(self) -> None:
        mixer = AudioMixer()
        mixer.set_tracks([MixerTrack("a", np.full(500, 0.5, dtype=np.float32), 44100)])
        mixer.set_track_gain("a", 0.5)
        out = _decode(mixer.readData(500 * 8))
        np.testing.assert_allclose(out, 0.25, atol=1e-6)

    def test_gain_is_clamped(self) -> None:
        mixer = AudioMixer()
        mixer.set_tracks([MixerTrack("a", np.full(10, 0.5, dtype=np.float32), 44100)])
        mixer.set_track_gain("a", 5.0)
        mixer.set_track_gain("a", -1.0)
        out = _decode(mixer.readData(10 * 8))
        np.testing.assert_allclose(out, 0.0, atol=1e-6)

    def test_mute_excludes_track(self) -> None:
        mixer = AudioMixer()
        mixer.set_tracks(
            [
                MixerTrack("a", np.full(1000, 0.1, dtype=np.float32), 44100),
                MixerTrack("b", np.full(1000, 0.2, dtype=np.float32), 44100),
            ]
        )
        mixer.set_track_muted("a", True)
        out = _decode(mixer.readData(1000 * 8))
        np.testing.assert_allclose(out, 0.2, atol=1e-6)

    def test_clips_output_to_unit_range(self) -> None:
        mixer = AudioMixer()
        mixer.set_tracks([MixerTrack("a", np.full(100, 2.0, dtype=np.float32), 44100)])
        out = _decode(mixer.readData(100 * 8))
        np.testing.assert_allclose(out, 1.0, atol=1e-6)

    def test_seek_reads_from_offset(self) -> None:
        data = np.linspace(0.0, 1.0, 88_200, endpoint=False).astype(np.float32)
        mixer = AudioMixer()
        mixer.set_tracks([MixerTrack("a", data, 44100)])
        mixer.seek_ms(1000)
        out = _decode(mixer.readData(16 * 8))
        np.testing.assert_allclose(out[:, 0], data[44_100:44_116], atol=1e-6)

    def test_set_active_filters_tracks(self) -> None:
        mixer = AudioMixer()
        mixer.set_tracks(
            [
                MixerTrack("a", np.full(1000, 0.1, dtype=np.float32), 44100),
                MixerTrack("b", np.full(1000, 0.2, dtype=np.float32), 44100),
            ]
        )
        mixer.set_active(["a"])
        out = _decode(mixer.readData(1000 * 8))
        np.testing.assert_allclose(out, 0.1, atol=1e-6)
        assert mixer.active_stems() == ["a"]


class TestMixerState:
    """Tests for playback state, EOF and transport control."""

    def test_duration_is_max_of_tracks(self) -> None:
        mixer = AudioMixer()
        mixer.set_tracks(
            [
                MixerTrack("a", np.zeros(44_100, dtype=np.float32), 44100),
                MixerTrack("b", np.zeros(88_200, dtype=np.float32), 44100),
            ]
        )
        assert mixer.duration_ms() == 2000

    def test_set_tracks_emits_duration_changed(self) -> None:
        mixer = AudioMixer()
        durations: list[int] = []
        mixer.duration_changed.connect(durations.append)
        mixer.set_tracks([MixerTrack("a", np.zeros(44_100, dtype=np.float32), 44100)])
        assert durations == [1000]

    def test_play_no_tracks_is_noop(self) -> None:
        mixer = AudioMixer()
        mixer.play()
        assert mixer.state == PlaybackState.STOPPED

    def test_play_pause_stop_transitions(self, qapp) -> None:
        mixer, sink = _mixer_with_playback_sink()
        states: list[PlaybackState] = []
        mixer.state_changed.connect(states.append)

        mixer.play()
        assert sink.started == 1
        assert mixer.state == PlaybackState.PLAYING

        mixer.pause()
        assert sink.suspended == 1
        assert mixer.state == PlaybackState.PAUSED

        mixer.play()
        assert sink.resumed == 1
        assert mixer.state == PlaybackState.PLAYING

        mixer.stop()
        assert sink.stopped == 1
        assert mixer.state == PlaybackState.STOPPED
        assert mixer.position_ms() == 0
        assert PlaybackState.STOPPED in states

    def test_pause_is_noop_when_stopped(self, qapp) -> None:
        mixer, sink = _mixer_with_playback_sink()
        mixer.pause()
        assert sink.suspended == 0
        assert mixer.state == PlaybackState.STOPPED

    def test_stop_resets_position(self, qapp) -> None:
        mixer, _ = _mixer_with_playback_sink()
        mixer.seek_ms(500)
        assert mixer.position_ms() == 500
        mixer.stop()
        assert mixer.position_ms() == 0

    def test_eof_flags_stopped_via_timer(self, qapp) -> None:
        mixer = AudioMixer(sink_factory=lambda fmt: FakeSink())
        mixer.set_tracks([MixerTrack("a", np.ones(1000, dtype=np.float32), 44100)])
        mixer._sink = mixer._sink_factory(None)
        mixer._ensure_sink = lambda: True  # type: ignore[method-assign]
        mixer.play()
        mixer.readData(1000 * 8)
        states: list[PlaybackState] = []
        mixer.state_changed.connect(states.append)
        mixer._on_timer()
        assert mixer._sink.stopped == 1
        assert mixer.state == PlaybackState.STOPPED
        assert PlaybackState.STOPPED in states

    def test_eof_ignored_when_not_playing(self, qapp) -> None:
        mixer = AudioMixer(sink_factory=lambda fmt: FakeSink())
        mixer.set_tracks([MixerTrack("a", np.ones(1000, dtype=np.float32), 44100)])
        mixer._sink = mixer._sink_factory(None)
        mixer._ensure_sink = lambda: True  # type: ignore[method-assign]
        mixer.readData(1000 * 8)
        mixer._on_timer()
        assert mixer.state == PlaybackState.STOPPED
        assert mixer._sink.stopped == 0

    def test_seek_emits_position_changed(self) -> None:
        mixer = AudioMixer()
        mixer.set_tracks([MixerTrack("a", np.zeros(88_200, dtype=np.float32), 44100)])
        positions: list[int] = []
        mixer.position_changed.connect(positions.append)
        mixer.seek_ms(1000)
        assert positions == [1000]

    def test_master_volume_delegates_to_sink(self, qapp) -> None:
        mixer, sink = _mixer_with_playback_sink()
        mixer.set_master_volume(0.5)
        assert sink.volume == 0.5

    def test_state_changed_emitted_on_transition_only(self, qapp) -> None:
        mixer = AudioMixer(sink_factory=lambda fmt: FakeSink())
        mixer.set_tracks([MixerTrack("a", np.ones(1000, dtype=np.float32), 44100)])
        mixer._sink = mixer._sink_factory(None)
        mixer._ensure_sink = lambda: True  # type: ignore[method-assign]
        states: list[PlaybackState] = []
        mixer.state_changed.connect(states.append)
        mixer.play()
        mixer.play()
        mixer.stop()
        assert states == [PlaybackState.PLAYING, PlaybackState.STOPPED]


class TestEnsureSink:
    """Tests for the lazy sink creation."""

    def test_no_device_sets_error_state(self, monkeypatch) -> None:
        class _Device:
            def isNull(self) -> bool:
                return True

        class _Devices:
            @staticmethod
            def defaultAudioOutput() -> _Device:
                return _Device()

        monkeypatch.setattr("app.audio.mixer.QMediaDevices", _Devices)
        mixer = AudioMixer()
        mixer.set_tracks([MixerTrack("a", np.ones(1000, dtype=np.float32), 44100)])
        errors: list[str] = []
        mixer.error_occurred.connect(errors.append)
        assert not mixer._ensure_sink()
        assert mixer.state == PlaybackState.ERROR
        assert errors
