"""Local test fixtures for audio module tests."""

from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def sample_wav_path() -> Path:
    """Path to mono WAV fixture."""
    return Path("tests/fixtures/sample.wav")


@pytest.fixture
def sample_stereo_path() -> Path:
    """Path to stereo WAV fixture."""
    return Path("tests/fixtures/sample_stereo.wav")


@pytest.fixture
def mono_audio_3s() -> np.ndarray:
    """3 seconds of mono sine wave at 44100 Hz."""
    return np.sin(2 * np.pi * 440 * np.linspace(0, 3, 44100 * 3)).astype(np.float32)


@pytest.fixture
def stereo_audio_2s() -> np.ndarray:
    """2 seconds of stereo sine wave at 44100 Hz."""
    t = np.linspace(0, 2, 44100 * 2)
    left = np.sin(2 * np.pi * 440 * t).astype(np.float32)
    right = np.sin(2 * np.pi * 880 * t).astype(np.float32)
    return np.stack([left, right])


@pytest.fixture
def silent_audio() -> np.ndarray:
    """3 seconds of silence."""
    return np.zeros(44100 * 3, dtype=np.float32)


@pytest.fixture
def dc_offset_audio() -> np.ndarray:
    """Audio with DC offset of 0.5."""
    return (np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100)) + 0.5).astype(np.float32)
