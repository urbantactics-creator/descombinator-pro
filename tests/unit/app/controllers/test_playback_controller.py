"""Tests for the PlaybackController."""

from __future__ import annotations

import json

import numpy as np
from PySide6.QtCore import QObject, Signal

from app.audio.mixer import PlaybackState
from app.controllers.playback_controller import PlaybackController
from app.services.playback_state_store import PlaybackStateStore


class FakeService(QObject):
    """In-memory fake of PlaybackService exposing the same interface."""

    state_changed = Signal(PlaybackState)
    position_changed = Signal(int)
    duration_changed = Signal(int)
    error_occurred = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._tracks: dict[str, dict] = {}
        self._active: list[str] = []
        self._state = PlaybackState.STOPPED
        self._position = 0

    def set_source(self, audio: np.ndarray, sample_rate: int) -> None:
        self._tracks = {"source": {"volume": 1.0, "muted": False}}
        self._active = ["source"]

    def set_stems(
        self, stems: dict[str, np.ndarray], sample_rate: int = 44_100
    ) -> None:
        self._tracks = {name: {"volume": 1.0, "muted": False} for name in stems}
        self._active = list(stems)

    def set_track_volume(self, name: str, volume: float) -> None:
        if name in self._tracks:
            self._tracks[name]["volume"] = volume

    def set_track_muted(self, name: str, muted: bool) -> None:
        if name in self._tracks:
            self._tracks[name]["muted"] = muted

    def set_active_stems(self, names: list[str]) -> None:
        self._active = list(names)

    def set_master_volume(self, volume: float) -> None:
        self.master_volume = volume

    def play(self) -> None:
        self._state = PlaybackState.PLAYING

    def pause(self) -> None:
        self._state = PlaybackState.PAUSED

    def stop(self) -> None:
        self._state = PlaybackState.STOPPED

    def seek_ms(self, ms: int) -> None:
        self._position = ms

    def set_position(self, ms: int) -> None:
        self.seek_ms(ms)

    def clear(self) -> None:
        self._tracks = {}
        self._active = []

    def get_state(self) -> PlaybackState:
        return self._state

    def get_position(self) -> int:
        return self._position

    def get_duration(self) -> int:
        return 0

    def has_tracks(self) -> bool:
        return bool(self._tracks)

    def has_stems(self) -> bool:
        return bool(self._tracks) and set(self._tracks) != {"source"}

    def track_names(self) -> list[str]:
        return list(self._tracks)

    def track_volumes(self) -> dict[str, float]:
        return {name: t["volume"] for name, t in self._tracks.items()}

    def muted_map(self) -> dict[str, bool]:
        return {name: t["muted"] for name, t in self._tracks.items()}

    def active_stems(self) -> list[str]:
        return self._active


class TestPlaybackControllerInit:
    """Tests for PlaybackController initialization."""

    def test_creates_without_error(self) -> None:
        ctrl = PlaybackController()
        assert ctrl is not None

    def test_initial_state_is_stopped(self) -> None:
        ctrl = PlaybackController()
        assert ctrl.get_state() == "stopped"

    def test_injected_service_is_used(self) -> None:
        service = FakeService()
        ctrl = PlaybackController(service=service, store=PlaybackStateStore())
        assert ctrl._service is service


class TestPlaybackControllerPlayPause:
    """Tests for play/pause/stop."""

    def test_play_starts_playing(self, qapp) -> None:
        ctrl = PlaybackController()
        ctrl.play()
        # Without media loaded, play is a no-op
        assert ctrl.get_state() == "stopped"

    def test_pause_is_noop_when_stopped(self) -> None:
        ctrl = PlaybackController()
        ctrl.pause()
        assert ctrl.get_state() == "stopped"

    def test_stop_is_noop_when_stopped(self) -> None:
        ctrl = PlaybackController()
        ctrl.stop()
        assert ctrl.get_state() == "stopped"


class TestPlaybackControllerPosition:
    """Tests for position and volume."""

    def test_set_position_no_crash(self) -> None:
        ctrl = PlaybackController()
        ctrl.set_position(1000)
        # The mixer stores the seek position even without loaded media
        assert ctrl.get_position() == 1000

    def test_set_volume_no_crash(self) -> None:
        ctrl = PlaybackController()
        ctrl.set_volume(0.5)

    def test_set_volume_emits_master_volume_changed(self) -> None:
        service = FakeService()
        ctrl = PlaybackController(service=service, store=PlaybackStateStore())
        volumes: list[float] = []
        ctrl.master_volume_changed.connect(volumes.append)
        ctrl.set_volume(0.5)
        assert volumes == [0.5]
        assert service.master_volume == 0.5

    def test_seek_ms_forwards_to_service(self) -> None:
        service = FakeService()
        ctrl = PlaybackController(service=service, store=PlaybackStateStore())
        ctrl.seek_ms(2500)
        assert service.get_position() == 2500


class TestPlaybackControllerStems:
    """Tests for multi-track stem handling and persistence."""

    def test_set_stems_emits_tracks_changed(self, tmp_path) -> None:
        service = FakeService()
        ctrl = PlaybackController(
            service=service, store=PlaybackStateStore(tmp_path / "state.json")
        )
        changed: list[list[str]] = []
        ctrl.tracks_changed.connect(changed.append)
        ctrl.set_stems({"vocals": np.zeros(100), "bass": np.zeros(100)})
        assert changed == [["vocals", "bass"]]
        assert service.active_stems() == ["vocals", "bass"]

    def test_set_stems_restores_volumes_from_store(self, tmp_path) -> None:
        path = tmp_path / "state.json"
        path.write_text(json.dumps({"volumes": {"vocals": 0.3}}))
        service = FakeService()
        ctrl = PlaybackController(service=service, store=PlaybackStateStore(path))
        ctrl.set_stems({"vocals": np.zeros(100), "bass": np.zeros(100)})
        assert service.track_volumes()["vocals"] == 0.3
        assert service.track_volumes()["bass"] == 1.0

    def test_set_stems_restores_muted_and_active(self, tmp_path) -> None:
        path = tmp_path / "state.json"
        path.write_text(
            json.dumps({"muted": {"bass": True}, "active_stems": ["vocals"]})
        )
        service = FakeService()
        ctrl = PlaybackController(service=service, store=PlaybackStateStore(path))
        ctrl.set_stems({"vocals": np.zeros(100), "bass": np.zeros(100)})
        assert service.muted_map()["bass"] is True
        assert service.active_stems() == ["vocals"]

    def test_set_track_volume_emits_and_schedules_save(self, tmp_path) -> None:
        store = PlaybackStateStore(tmp_path / "state.json")
        service = FakeService()
        ctrl = PlaybackController(service=service, store=store)
        ctrl.set_stems({"vocals": np.zeros(100)})
        volumes: list[tuple[str, float]] = []
        ctrl.track_volume_changed.connect(lambda n, v: volumes.append((n, v)))
        ctrl.set_track_volume("vocals", 0.7)
        assert volumes == [("vocals", 0.7)]
        assert ctrl._save_timer.isActive()
        ctrl._flush_save()
        assert store.load()["volumes"] == {"vocals": 0.7}

    def test_set_track_muted_emits_and_schedules_save(self, tmp_path) -> None:
        store = PlaybackStateStore(tmp_path / "state.json")
        service = FakeService()
        ctrl = PlaybackController(service=service, store=store)
        ctrl.set_stems({"vocals": np.zeros(100)})
        muted: list[tuple[str, bool]] = []
        ctrl.track_muted_changed.connect(lambda n, m: muted.append((n, m)))
        ctrl.set_track_muted("vocals", True)
        assert muted == [("vocals", True)]
        ctrl._flush_save()
        assert store.load()["muted"] == {"vocals": True}

    def test_set_active_stems_persists_immediately(self, tmp_path) -> None:
        store = PlaybackStateStore(tmp_path / "state.json")
        service = FakeService()
        ctrl = PlaybackController(service=service, store=store)
        ctrl.set_stems({"vocals": np.zeros(100), "bass": np.zeros(100)})
        ctrl.set_active_stems(["bass"])
        assert store.load()["active_stems"] == ["bass"]
        assert service.active_stems() == ["bass"]

    def test_round_trip_restores_state(self, tmp_path) -> None:
        path = tmp_path / "state.json"
        service = FakeService()
        ctrl = PlaybackController(service=service, store=PlaybackStateStore(path))
        ctrl.set_stems({"vocals": np.zeros(100), "bass": np.zeros(100)})
        ctrl.set_track_volume("vocals", 0.7)
        ctrl.set_track_muted("bass", True)
        ctrl.set_active_stems(["vocals"])
        ctrl._flush_save()

        service2 = FakeService()
        ctrl2 = PlaybackController(service=service2, store=PlaybackStateStore(path))
        ctrl2.set_stems({"vocals": np.zeros(100), "bass": np.zeros(100)})
        assert service2.track_volumes()["vocals"] == 0.7
        assert service2.muted_map()["bass"] is True
        assert service2.active_stems() == ["vocals"]

    def test_reset_clears_tracks_and_persists(self, tmp_path) -> None:
        store = PlaybackStateStore(tmp_path / "state.json")
        service = FakeService()
        ctrl = PlaybackController(service=service, store=store)
        ctrl.set_stems({"vocals": np.zeros(100)})
        ctrl.reset()
        assert service.track_names() == []
        assert not ctrl._save_timer.isActive()
        assert store.load()["active_stems"] == []

    def test_record_last_file_persists_immediately(self, tmp_path) -> None:
        store = PlaybackStateStore(tmp_path / "state.json")
        ctrl = PlaybackController(service=FakeService(), store=store)
        ctrl.record_last_file("/music/song.wav")
        assert store.load()["last_file"] == "/music/song.wav"

    def test_has_stems_reflects_service(self) -> None:
        service = FakeService()
        ctrl = PlaybackController(service=service, store=PlaybackStateStore())
        assert not ctrl.has_stems()
        ctrl.set_stems({"vocals": np.zeros(100)})
        assert ctrl.has_stems()
