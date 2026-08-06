"""UI integration tests exercising the real playback stack headless.

These tests use real ``PlaybackService`` / ``PlaybackController`` /
``PlaybackStateStore`` / ``AudioMixer`` instances (no mocks) so the playback
stack is exercised end-to-end without an audio device. The mixer only creates
its sink lazily on ``play()``, which makes this safe in headless CI.
"""

from pathlib import Path

import numpy as np

from app.audio.mixer import PlaybackState
from app.controllers.playback_controller import PlaybackController
from app.services.playback_service import PlaybackService
from app.services.playback_state_store import PlaybackStateStore


def _make_controller(tmp_path: Path) -> tuple[PlaybackController, PlaybackStateStore]:
    store = PlaybackStateStore(path=tmp_path / "state.json")
    service = PlaybackService()
    controller = PlaybackController(service=service, store=store)
    return controller, store


def test_playback_set_source(qapp, tmp_path):
    """Test setting a source track through the controller."""
    controller, _ = _make_controller(tmp_path)
    audio = np.zeros(44100, dtype=np.float32)
    controller.set_source(audio, 44100)
    assert controller.track_names() == ["source"]
    assert controller.has_media()
    assert not controller.has_stems()


def test_playback_set_stems_persists(qapp, tmp_path):
    """Test setting stems restores persisted per-track state."""
    controller, store = _make_controller(tmp_path)
    store.save(
        volumes={"vocals": 0.5, "drums": 0.25},
        muted={"bass": True},
        active_stems=["vocals"],
        last_file="song.wav",
    )

    stems = {
        "vocals": np.zeros(44100, dtype=np.float32),
        "drums": np.zeros(44100, dtype=np.float32),
        "bass": np.zeros(44100, dtype=np.float32),
    }
    controller.set_stems(stems)

    assert controller.track_names() == ["vocals", "drums", "bass"]
    assert controller.track_volumes()["vocals"] == 0.5
    assert controller.muted_map()["bass"] is True
    assert controller.active_stems() == ["vocals"]
    assert controller.has_stems()


def test_playback_volume_mute_roundtrip(qapp, tmp_path):
    """Test volume/mute changes persist to disk after flush."""
    controller, store = _make_controller(tmp_path)
    controller.set_stems({"vocals": np.zeros(44100, dtype=np.float32)})

    controller.set_track_volume("vocals", 0.7)
    controller.set_track_muted("vocals", True)
    controller._flush_save()

    loaded = store.load()
    assert loaded["volumes"]["vocals"] == 0.7
    assert loaded["muted"]["vocals"] is True


def test_playback_active_stems_persist_immediately(qapp, tmp_path):
    """Test active stems are persisted immediately."""
    controller, store = _make_controller(tmp_path)
    stems = {
        "vocals": np.zeros(44100, dtype=np.float32),
        "drums": np.zeros(44100, dtype=np.float32),
    }
    controller.set_stems(stems)
    controller.set_active_stems(["drums"])
    loaded = store.load()
    assert loaded["active_stems"] == ["drums"]


def test_playback_record_last_file(qapp, tmp_path):
    """Test the last file is persisted."""
    controller, store = _make_controller(tmp_path)
    controller.record_last_file("/tmp/song.wav")
    assert store.load()["last_file"] == "/tmp/song.wav"


def test_playback_state_transitions(qapp, tmp_path):
    """Test play/pause/stop state transitions on a real mixer."""
    controller, _ = _make_controller(tmp_path)
    controller.set_stems({"vocals": np.zeros(44100, dtype=np.float32)})

    controller.play()
    state = controller.get_state()
    assert state in (PlaybackState.PLAYING.value, PlaybackState.ERROR.value)

    controller.pause()
    controller.stop()
    assert controller.get_state() == PlaybackState.STOPPED.value


def test_playback_seek_position(qapp, tmp_path):
    """Test seek and position reporting."""
    controller, _ = _make_controller(tmp_path)
    audio = np.zeros(44100, dtype=np.float32)
    controller.set_source(audio, 44100)

    controller.seek_ms(5_000)
    assert controller.get_position() == 5_000

    controller.set_position(0)
    assert controller.get_position() == 0


def test_playback_master_volume(qapp, tmp_path):
    """Test master volume setters do not raise."""
    controller, _ = _make_controller(tmp_path)
    controller.set_master_volume(0.8)
    controller.set_volume(0.5)
    assert controller is not None


def test_playback_reset(qapp, tmp_path):
    """Test reset clears tracks and persists a clean snapshot."""
    controller, store = _make_controller(tmp_path)
    controller.set_stems({"vocals": np.zeros(44100, dtype=np.float32)})
    controller.reset()
    assert controller.track_names() == []
    loaded = store.load()
    assert loaded["active_stems"] == []
    assert loaded["last_file"] is None


def test_playback_stereo_source_to_mono(qapp, tmp_path):
    """Test stereo source is reduced to mono in the mixer."""
    controller, _ = _make_controller(tmp_path)
    stereo = np.zeros((2, 44100), dtype=np.float32)
    controller.set_source(stereo, 44100)
    assert controller.get_duration() == 1000


def test_playback_stems_resampled(qapp, tmp_path):
    """Test stems at a non-44.1k rate are resampled by the service."""
    service = PlaybackService()
    service.set_stems({"vocals": np.zeros(22050, dtype=np.float32)}, sample_rate=22050)
    assert service.track_names() == ["vocals"]
    assert service.get_duration() == 1000


def test_playback_getters(qapp, tmp_path):
    """Test the remaining read-only getters."""
    controller, _ = _make_controller(tmp_path)
    stems = {
        "vocals": np.zeros(44100, dtype=np.float32),
        "drums": np.zeros(44100, dtype=np.float32),
    }
    controller.set_stems(stems)
    assert set(controller.track_names()) == {"vocals", "drums"}
    assert controller.muted_map() == {"vocals": False, "drums": False}
    assert set(controller.active_stems()) == {"vocals", "drums"}
    assert controller.has_stems()
    assert controller.has_media()
