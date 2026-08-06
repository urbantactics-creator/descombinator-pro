"""Local test fixtures for inference module tests."""

import numpy as np
import pytest
import torch

from engine.inference.config import InferenceConfig, ModelName


@pytest.fixture
def dummy_audio_numpy() -> np.ndarray:
    """1 second of mono sine wave at 44100 Hz."""
    return np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100)).astype(np.float32)


@pytest.fixture
def dummy_audio_torch() -> torch.Tensor:
    """1 second of stereo sine wave as torch tensor (channels, samples)."""
    t = torch.linspace(0, 1, 44100)
    left = torch.sin(2 * np.pi * 440 * t)
    right = torch.sin(2 * np.pi * 880 * t)
    return torch.stack([left, right])


@pytest.fixture
def default_config() -> InferenceConfig:
    """Default inference configuration."""
    return InferenceConfig()


@pytest.fixture
def demucs_config() -> InferenceConfig:
    """Demucs-specific inference configuration."""
    return InferenceConfig(model_name=ModelName.HTDEMUCS_FT)


@pytest.fixture
def openunmix_config() -> InferenceConfig:
    """Open-Unmix-specific inference configuration."""
    return InferenceConfig(model_name=ModelName.UMXHQ)
