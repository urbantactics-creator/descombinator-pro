"""Persistence store for playback state."""

import json
from pathlib import Path
from typing import Any

from loguru import logger


class PlaybackStateStore:
    """Persist per-track volumes, mutes, active stems and the last file.

    State is stored as JSON at ``~/.descombinator/playback_state.json`` by
    default, following the same pattern as ``SettingsController``. All I/O
    errors are logged and swallowed so a corrupt or missing file never
    breaks playback.
    """

    _DEFAULTS: dict[str, Any] = {
        "volumes": {},
        "muted": {},
        "active_stems": [],
        "last_file": None,
    }

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or Path.home() / ".descombinator" / "playback_state.json"

    @property
    def path(self) -> Path:
        """Path of the persisted state file."""
        return self._path

    def load(self) -> dict[str, Any]:
        """Load playback state, merging with defaults on missing/corrupt data."""
        data = dict(self._DEFAULTS)
        try:
            if not self._path.exists():
                return data
            with open(self._path) as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                data.update(loaded)
            if not isinstance(data["volumes"], dict):
                data["volumes"] = {}
            if not isinstance(data["muted"], dict):
                data["muted"] = {}
            if not isinstance(data["active_stems"], list):
                data["active_stems"] = []
            return data
        except Exception as e:
            logger.warning(f"Failed to load playback state from {self._path}: {e}")
            return dict(self._DEFAULTS)

    def save(
        self,
        volumes: dict[str, float],
        muted: dict[str, bool],
        active_stems: list[str],
        last_file: str | None,
    ) -> None:
        """Persist playback state to JSON."""
        data = {
            "volumes": volumes,
            "muted": muted,
            "active_stems": active_stems,
            "last_file": last_file,
        }
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save playback state to {self._path}: {e}")
