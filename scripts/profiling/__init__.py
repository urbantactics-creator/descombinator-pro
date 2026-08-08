"""Shared helpers for profiling scripts.

Importable from ``scripts/profiling`` and ``scripts/bench``. Kept free of
heavy third-party imports (torch/librosa) so it can load instantly.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def ensure_project_root() -> None:
    """Insert the project root into sys.path so ``engine``/``app`` resolve."""
    root = str(PROJECT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def env_int(name: str, default: int) -> int:
    """Read an integer from the environment with a fallback."""
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default
