"""Unit tests for AudioMixer and MixerTrack."""

import numpy as np
from PySide6.QtMultimedia import QAudioFormat

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

    def test_readData_empty_chunk_does_not_modify_output(self) -> None:
        """When a track is shorter than the requested frames, the empty
        chunk branch (line 111) must be taken without raising."""
        mixer = AudioMixer()
        mixer.set_tracks([MixerTrack("a", np.ones(5, dtype=np.float32), 44100)])
        out = _decode(mixer.readData(1000 * 8))
        assert out.shape == (1000, 2)
        np.testing.assert_allclose(out[:5], 1.0, atol=1e-6)
        np.testing.assert_allclose(out[5:], 0.0, atol=1e-6)

    def test_readData_empty_chunk_between_tracks(self) -> None:
        """When a short track is exhausted, the empty chunk branch must
        continue to the next track in the loop (line 111->107)."""
        mixer = AudioMixer()
        mixer.set_tracks(
            [
                MixerTrack("a", np.full(5, 0.1, dtype=np.float32), 44100),
                MixerTrack("b", np.full(1000, 0.2, dtype=np.float32), 44100),
            ]
        )
        mixer._position_frames = 5
        out = _decode(mixer.readData(1000 * 8))
        assert out.shape == (1000, 2)
        np.testing.assert_allclose(out[:995, 0], 0.2, atol=1e-6)
        np.testing.assert_allclose(out[995:, 0], 0.0, atol=1e-6)

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

    def test_readData_int16_branch(self) -> None:
        """Cover the Int16 encoding branch (line 119)."""
        mixer = AudioMixer()
        mixer._bytes_per_frame = mixer.CHANNELS * 2  # _INT16_BYTES
        mixer.set_tracks([MixerTrack("a", np.full(100, 0.5, dtype=np.float32), 44100)])
        raw = mixer.readData(100 * mixer._bytes_per_frame)
        decoded = np.frombuffer(raw, dtype=np.int16).reshape(-1, 2)
        expected = np.int16(np.clip(0.5, -1.0, 1.0) * 32767)
        np.testing.assert_allclose(decoded, expected, atol=1)


class TestWriteData:
    """Tests for the unsupported write path."""

    def test_writeData_returns_zero(self) -> None:
        mixer = AudioMixer()
        assert mixer.writeData(b"anything") == 0


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

    def test_set_tracks_stops_when_playing(self, qapp) -> None:
        """set_tracks must stop playback if the mixer is not STOPPED."""
        mixer, sink = _mixer_with_playback_sink()
        mixer.play()
        assert mixer.state == PlaybackState.PLAYING
        mixer.set_tracks([MixerTrack("b", np.ones(100, dtype=np.float32), 44100)])
        assert mixer.state == PlaybackState.STOPPED
        assert sink.stopped == 1

    def test_set_active_stops_when_playing(self, qapp) -> None:
        """set_active must stop playback if the mixer is not STOPPED."""
        mixer, sink = _mixer_with_playback_sink()
        mixer.play()
        assert mixer.state == PlaybackState.PLAYING
        mixer.set_active([])
        assert mixer.state == PlaybackState.STOPPED
        assert sink.stopped == 1

    def test_play_returns_early_when_sink_creation_fails(self, qapp) -> None:
        """play() must return early when _ensure_sink returns False (line 170)."""
        mixer = AudioMixer(sink_factory=lambda fmt: FakeSink())
        mixer.set_tracks([MixerTrack("a", np.ones(100, dtype=np.float32), 44100)])
        mixer._ensure_sink = lambda: False  # type: ignore[method-assign]
        mixer.play()
        assert mixer.state == PlaybackState.STOPPED

    def test_play_resets_position_when_at_end(self, qapp) -> None:
        """play() must reset position to 0 when already at EOF (line 177)."""
        mixer, sink = _mixer_with_playback_sink()
        mixer.seek_ms(2000)
        assert mixer.position_ms() == 2000
        mixer.play()
        assert mixer.position_ms() == 0
        assert mixer.state == PlaybackState.PLAYING

    def test_stop_is_safe_without_sink(self) -> None:
        """stop() must not crash when _sink is None (lines 192-194)."""
        mixer = AudioMixer()
        mixer.stop()
        assert mixer.state == PlaybackState.STOPPED
        assert mixer.position_ms() == 0

    def test_set_master_volume_is_noop_without_sink(self) -> None:
        """set_master_volume must not crash when _sink is None (line 210)."""
        mixer = AudioMixer()
        mixer.set_master_volume(0.5)
        assert mixer.state == PlaybackState.STOPPED

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

    def test_on_timer_handles_none_sink_at_eof(self, qapp) -> None:
        """_on_timer must not crash when EOF reached but _sink is None."""
        mixer = AudioMixer(sink_factory=lambda fmt: FakeSink())
        mixer.set_tracks([MixerTrack("a", np.ones(100, dtype=np.float32), 44100)])
        mixer._sink = None
        mixer._ensure_sink = lambda: True  # type: ignore[method-assign]
        mixer._set_state(PlaybackState.PLAYING)
        mixer._eof = True
        mixer._on_timer()
        assert mixer.state == PlaybackState.STOPPED

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

    def test_set_track_gain_missing_track_is_noop(self) -> None:
        """set_track_gain must not crash when track name is missing (line 142)."""
        mixer = AudioMixer()
        mixer.set_tracks([MixerTrack("a", np.ones(100, dtype=np.float32), 44100)])
        mixer.set_track_gain("nonexistent", 0.5)
        assert mixer.state == PlaybackState.STOPPED

    def test_set_track_muted_missing_track_is_noop(self) -> None:
        """set_track_muted must not crash when track name is missing (line 149)."""
        mixer = AudioMixer()
        mixer.set_tracks([MixerTrack("a", np.ones(100, dtype=np.float32), 44100)])
        mixer.set_track_muted("nonexistent", True)
        assert mixer.state == PlaybackState.STOPPED


class TestMixerProperties:
    """Tests for query properties exposed by AudioMixer."""

    def test_track_names_returns_loaded_names(self) -> None:
        mixer = AudioMixer()
        mixer.set_tracks(
            [
                MixerTrack("a", np.ones(100, dtype=np.float32), 44100),
                MixerTrack("b", np.ones(100, dtype=np.float32), 44100),
            ]
        )
        assert mixer.track_names() == ["a", "b"]

    def test_track_gains_returns_current_gains(self) -> None:
        mixer = AudioMixer()
        mixer.set_tracks([MixerTrack("a", np.ones(100, dtype=np.float32), 44100)])
        mixer.set_track_gain("a", 0.7)
        assert mixer.track_gains() == {"a": 0.7}

    def test_track_muted_map_returns_mute_state(self) -> None:
        mixer = AudioMixer()
        mixer.set_tracks([MixerTrack("a", np.ones(100, dtype=np.float32), 44100)])
        mixer.set_track_muted("a", True)
        assert mixer.track_muted_map() == {"a": True}


class TestBuildFormat:
    """Tests for the private _build_format helper."""

    def test_default_format_is_float(self) -> None:
        mixer = AudioMixer()
        fmt = mixer._build_format()
        assert fmt.sampleRate() == mixer.SAMPLE_RATE
        assert fmt.channelCount() == mixer.CHANNELS
        assert fmt.sampleFormat() == QAudioFormat.SampleFormat.Float

    def test_int16_format(self) -> None:
        mixer = AudioMixer()
        fmt = mixer._build_format(QAudioFormat.SampleFormat.Int16)
        assert fmt.sampleFormat() == QAudioFormat.SampleFormat.Int16


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

    def test_format_factory_is_used(self, monkeypatch) -> None:
        """_ensure_sink must use format_factory when provided (line 269)."""
        created_fmts: list[QAudioFormat] = []

        def fake_factory() -> QAudioFormat:
            fmt = QAudioFormat()
            fmt.setSampleRate(48_000)
            fmt.setChannelCount(2)
            fmt.setSampleFormat(QAudioFormat.SampleFormat.Float)
            created_fmts.append(fmt)
            return fmt

        class _Device:
            def isNull(self) -> bool:
                return False

            def isFormatSupported(self, fmt: QAudioFormat) -> bool:
                return True

        class _Devices:
            @staticmethod
            def defaultAudioOutput() -> _Device:
                return _Device()

        monkeypatch.setattr("app.audio.mixer.QMediaDevices", _Devices)
        mixer = AudioMixer(
            format_factory=fake_factory, sink_factory=lambda fmt: FakeSink()
        )
        mixer.set_tracks([MixerTrack("a", np.ones(100, dtype=np.float32), 44100)])
        assert mixer._ensure_sink()
        assert len(created_fmts) == 1
        assert created_fmts[0].sampleRate() == 48_000

    def test_fallback_to_int16_when_not_supported(self, monkeypatch) -> None:
        """_ensure_sink must fall back to Int16 when Float is unsupported (line 274)."""
        build_calls: list[QAudioFormat.SampleFormat] = []
        original_build_format = AudioMixer._build_format

        def fake_build_format(
            self,
            sample_format: QAudioFormat.SampleFormat = QAudioFormat.SampleFormat.Float,
        ) -> QAudioFormat:
            build_calls.append(sample_format)
            return original_build_format(self, sample_format)

        monkeypatch.setattr(AudioMixer, "_build_format", fake_build_format)

        class _Device:
            def isNull(self) -> bool:
                return False

            def isFormatSupported(self, fmt: QAudioFormat) -> bool:
                return fmt.sampleFormat() == QAudioFormat.SampleFormat.Int16

        class _Devices:
            @staticmethod
            def defaultAudioOutput() -> _Device:
                return _Device()

        monkeypatch.setattr("app.audio.mixer.QMediaDevices", _Devices)
        mixer = AudioMixer(sink_factory=lambda fmt: FakeSink())
        mixer.set_tracks([MixerTrack("a", np.ones(100, dtype=np.float32), 44100)])
        assert mixer._ensure_sink()
        assert mixer._bytes_per_frame == mixer.CHANNELS * 2
        assert len(build_calls) == 2
        assert build_calls[0] == QAudioFormat.SampleFormat.Float
        assert build_calls[1] == QAudioFormat.SampleFormat.Int16

    def test_sink_factory_is_used(self, monkeypatch) -> None:
        """_ensure_sink must use sink_factory when provided (line 277-278)."""
        sinks: list[FakeSink] = []

        def fake_sink(fmt: QAudioFormat) -> FakeSink:
            sinks.append(FakeSink())
            return sinks[-1]

        class _Device:
            def isNull(self) -> bool:
                return False

            def isFormatSupported(self, fmt: QAudioFormat) -> bool:
                return True

        class _Devices:
            @staticmethod
            def defaultAudioOutput() -> _Device:
                return _Device()

        monkeypatch.setattr("app.audio.mixer.QMediaDevices", _Devices)
        mixer = AudioMixer(sink_factory=fake_sink)
        mixer.set_tracks([MixerTrack("a", np.ones(100, dtype=np.float32), 44100)])
        assert mixer._ensure_sink()
        assert len(sinks) == 1
        assert mixer._sink is sinks[-1]

    def test_ensure_sink_uses_real_qaudiosink_without_factory(
        self, monkeypatch
    ) -> None:
        """_ensure_sink must create QAudioSink when sink_factory is None (line 280)."""
        real_sinks: list = []

        class _FakeQAudioSink:
            def __init__(self, device, fmt) -> None:
                real_sinks.append(self)
                self.device = device
                self.fmt = fmt

            def setVolume(self, v: float) -> None:
                pass

            def start(self, device) -> None:
                pass

        class _Device:
            def isNull(self) -> bool:
                return False

            def isFormatSupported(self, fmt: QAudioFormat) -> bool:
                return True

        class _Devices:
            @staticmethod
            def defaultAudioOutput() -> _Device:
                return _Device()

        monkeypatch.setattr("app.audio.mixer.QMediaDevices", _Devices)
        monkeypatch.setattr("app.audio.mixer.QAudioSink", _FakeQAudioSink)
        mixer = AudioMixer()
        mixer.set_tracks([MixerTrack("a", np.ones(100, dtype=np.float32), 44100)])
        assert mixer._ensure_sink()
        assert len(real_sinks) == 1
        assert isinstance(mixer._sink, _FakeQAudioSink)

    def test_on_timer_stops_sink_on_eof(self, qapp) -> None:
        """_on_timer must stop the sink when EOF is reached (lines 319-321)."""
        mixer = AudioMixer(sink_factory=lambda fmt: FakeSink())
        mixer.set_tracks([MixerTrack("a", np.ones(1000, dtype=np.float32), 44100)])
        mixer._sink = mixer._sink_factory(None)
        mixer._ensure_sink = lambda: True  # type: ignore[method-assign]
        mixer.play()
        mixer.readData(1000 * 8)
        mixer._on_timer()
        assert mixer._sink.stopped == 1
        assert mixer.state == PlaybackState.STOPPED
