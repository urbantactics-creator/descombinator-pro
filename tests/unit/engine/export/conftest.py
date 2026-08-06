"""Shared test fixtures and markers for export module."""

from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def sample_stem() -> np.ndarray:
    """Return a sample mono audio stem (440 Hz sine wave)."""
    return np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100)).astype(np.float32)


@pytest.fixture
def sample_stems_dict() -> dict[str, np.ndarray]:
    """Return a dict of sample stems."""
    return {
        "vocals": np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100)).astype(np.float32),
        "drums": np.sin(2 * np.pi * 220 * np.linspace(0, 1, 44100)).astype(np.float32),
        "bass": np.sin(2 * np.pi * 110 * np.linspace(0, 1, 44100)).astype(np.float32),
    }


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Return a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
