"""Unit tests for app.services.playback_state_store — PlaybackStateStore."""

from __future__ import annotations

import json
from pathlib import Path

from app.services.playback_state_store import PlaybackStateStore


class TestPlaybackStateStoreInit:
    def test_default_path(self) -> None:
        store = PlaybackStateStore()
        assert "playback_state.json" in str(store.path)

    def test_custom_path(self, tmp_path: Path) -> None:
        p = tmp_path / "custom.json"
        store = PlaybackStateStore(path=p)
        assert store.path == p


class TestPlaybackStateStoreLoad:
    def test_load_no_file(self, tmp_path: Path) -> None:
        store = PlaybackStateStore(path=tmp_path / "nonexistent.json")
        data = store.load()
        assert data["volumes"] == {}
        assert data["muted"] == {}
        assert data["active_stems"] == []
        assert data["last_file"] is None

    def test_load_valid_json(self, tmp_path: Path) -> None:
        p = tmp_path / "state.json"
        p.write_text(
            json.dumps(
                {
                    "volumes": {"vocals": 0.8},
                    "muted": {"drums": True},
                    "active_stems": ["vocals"],
                    "last_file": "/path/to/file.wav",
                }
            )
        )
        store = PlaybackStateStore(path=p)
        data = store.load()
        assert data["volumes"] == {"vocals": 0.8}
        assert data["muted"] == {"drums": True}
        assert data["active_stems"] == ["vocals"]
        assert data["last_file"] == "/path/to/file.wav"

    def test_load_corrupt_json(self, tmp_path: Path) -> None:
        p = tmp_path / "corrupt.json"
        p.write_text("not valid json {{{")
        store = PlaybackStateStore(path=p)
        data = store.load()
        assert data["volumes"] == {}

    def test_load_invalid_types_in_volumes(self, tmp_path: Path) -> None:
        p = tmp_path / "state.json"
        p.write_text(
            json.dumps(
                {
                    "volumes": "not a dict",
                    "muted": {},
                    "active_stems": [],
                }
            )
        )
        store = PlaybackStateStore(path=p)
        data = store.load()
        assert data["volumes"] == {}

    def test_load_invalid_types_in_active_stems(self, tmp_path: Path) -> None:
        p = tmp_path / "state.json"
        p.write_text(
            json.dumps(
                {
                    "volumes": {},
                    "muted": {},
                    "active_stems": "not a list",
                }
            )
        )
        store = PlaybackStateStore(path=p)
        data = store.load()
        assert data["active_stems"] == []

    def test_load_partial_json(self, tmp_path: Path) -> None:
        p = tmp_path / "partial.json"
        p.write_text(json.dumps({"volumes": {"bass": 0.5}}))
        store = PlaybackStateStore(path=p)
        data = store.load()
        assert data["volumes"] == {"bass": 0.5}
        assert data["muted"] == {}
        assert data["active_stems"] == []
        assert data["last_file"] is None


class TestPlaybackStateStoreSave:
    def test_save_creates_file(self, tmp_path: Path) -> None:
        p = tmp_path / "saved.json"
        store = PlaybackStateStore(path=p)
        store.save(
            volumes={"vocals": 0.9},
            muted={"drums": True},
            active_stems=["vocals"],
            last_file="test.wav",
        )
        assert p.exists()
        data = json.loads(p.read_text())
        assert data["volumes"] == {"vocals": 0.9}
        assert data["muted"] == {"drums": True}
        assert data["active_stems"] == ["vocals"]
        assert data["last_file"] == "test.wav"

    def test_save_creates_parent_dirs(self, tmp_path: Path) -> None:
        p = tmp_path / "deep" / "nested" / "state.json"
        store = PlaybackStateStore(path=p)
        store.save(volumes={}, muted={}, active_stems=[], last_file=None)
        assert p.exists()

    def test_save_overwrites_existing(self, tmp_path: Path) -> None:
        p = tmp_path / "state.json"
        store = PlaybackStateStore(path=p)
        store.save(volumes={"a": 1.0}, muted={}, active_stems=[], last_file=None)
        store.save(volumes={"b": 0.5}, muted={}, active_stems=[], last_file=None)
        data = json.loads(p.read_text())
        assert data["volumes"] == {"b": 0.5}

    def test_save_empty_state(self, tmp_path: Path) -> None:
        p = tmp_path / "empty.json"
        store = PlaybackStateStore(path=p)
        store.save(volumes={}, muted={}, active_stems=[], last_file=None)
        data = json.loads(p.read_text())
        assert data["volumes"] == {}
        assert data["last_file"] is None


class TestPlaybackStateStoreRoundtrip:
    def test_save_then_load(self, tmp_path: Path) -> None:
        p = tmp_path / "roundtrip.json"
        store = PlaybackStateStore(path=p)
        store.save(
            volumes={"vocals": 0.7, "drums": 0.3},
            muted={"bass": True},
            active_stems=["vocals", "drums"],
            last_file="/audio/test.mp3",
        )
        data = store.load()
        assert data["volumes"] == {"vocals": 0.7, "drums": 0.3}
        assert data["muted"] == {"bass": True}
        assert data["active_stems"] == ["vocals", "drums"]
        assert data["last_file"] == "/audio/test.mp3"
