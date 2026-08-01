"""Shared test fixtures and markers for the Descombinator Pro test suite."""

from __future__ import annotations

import pathlib
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest


@pytest.fixture
def sample_audio_path() -> pathlib.Path:
    """Return path to sample test audio file."""
    return pathlib.Path("tests/fixtures/sample.wav")


@pytest.fixture
def sample_stereo_path() -> pathlib.Path:
    """Return path to stereo sample test audio file."""
    return pathlib.Path("tests/fixtures/sample_stereo.wav")


@pytest.fixture
def sample_wav_path() -> pathlib.Path:
    """Path to mono WAV fixture."""
    return pathlib.Path("tests/fixtures/sample.wav")


@pytest.fixture
def sample_stereo_path() -> pathlib.Path:
    """Path to stereo WAV fixture."""
    return pathlib.Path("tests/fixtures/sample_stereo.wav")


@pytest.fixture
def test_metadata_mp3_path() -> pathlib.Path:
    """Path to MP3 fixture with metadata."""
    return pathlib.Path("tests/fixtures/test_metadata.mp3")


@pytest.fixture
def test_metadata_flac_path() -> pathlib.Path:
    """Path to FLAC fixture with metadata."""
    return pathlib.Path("tests/fixtures/test_metadata.flac")


@pytest.fixture
def test_empty_wav_path() -> pathlib.Path:
    """Path to empty WAV fixture."""
    return pathlib.Path("tests/fixtures/test_empty.wav")


@pytest.fixture
def test_corrupt_wav_path() -> pathlib.Path:
    """Path to corrupt WAV fixture."""
    return pathlib.Path("tests/fixtures/test_corrupt.wav")


@pytest.fixture
def tmp_output_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    """Return a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def temp_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    """Return a temporary directory for test files."""
    return tmp_path


@pytest.fixture
def dummy_audio_numpy() -> np.ndarray:
    """1 second of mono sine wave at 44100 Hz."""
    return np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100)).astype(np.float32)


@pytest.fixture
def dummy_audio_stereo() -> np.ndarray:
    """1 second of stereo sine wave at 44100 Hz."""
    t = np.linspace(0, 1, 44100)
    left = np.sin(2 * np.pi * 440 * t).astype(np.float32)
    right = np.sin(2 * np.pi * 880 * t).astype(np.float32)
    return np.stack([left, right])


@pytest.fixture
def mock_separation_service() -> MagicMock:
    """Mock SeparationService for UI tests."""
    service = MagicMock()
    service.separate = AsyncMock(
        return_value={
            "vocals": np.random.randn(44100).astype(np.float32),
            "other": np.random.randn(44100).astype(np.float32),
        }
    )
    service.initialize = AsyncMock()
    return service


@pytest.fixture
def mock_model_manager() -> MagicMock:
    """Mock ModelManager for pipeline tests."""
    manager = MagicMock()
    manager.current_model = MagicMock()
    manager.switch_model = AsyncMock(return_value=manager.current_model)
    return manager
