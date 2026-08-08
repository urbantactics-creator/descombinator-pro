"""Startup import tests.

These run in a fresh subprocess so other tests cannot contaminate
``sys.modules``. The goal: importing ``main`` must NOT load the heavy ML
stack (torch, librosa, demucs, openunmix) — the PEP 562 lazy re-export
gate for the < 3s startup target.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

_HEAVY = ("torch", "librosa", "demucs", "openunmix")

_PROBE = f"""
import sys
sys.argv = ["main"]
import main
for name in {_HEAVY!r}:
    if name in sys.modules:
        print(name, "LOADED")
"""


def _probe_modules() -> list[str]:
    result = subprocess.run(
        [sys.executable, "-c", _PROBE],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.split()[0] for line in result.stdout.splitlines() if "LOADED" in line]


class TestStartupLazyImports:
    """Importing main must not load heavy ML modules."""

    def test_heavy_modules_not_loaded(self) -> None:
        loaded = _probe_modules()
        assert loaded == [], f"Heavy modules loaded at startup: {loaded}"
