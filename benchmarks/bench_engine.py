"""Benchmarks for the inference engine with mocked models."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from engine.demucs.config import SeparationConfig
from engine.demucs.separator import DemucsSeparator
from engine.inference.pipeline import InferencePipeline

# Reuse a single event loop across benchmark iterations instead of creating
# one per call (asyncio.run). Loop creation is a measurable, noisy overhead
# on fast benchmarks and widens the median spread that the regression gate
# compares against.
_LOOP = asyncio.new_event_loop()


def _run(coro) -> object:
    return _LOOP.run_until_complete(coro)


@pytest.fixture
def mock_model_manager() -> MagicMock:
    manager = MagicMock()
    model = MagicMock()
    model.separate = AsyncMock(
        side_effect=lambda audio: {"vocals": audio, "other": audio}
    )
    manager.current_model = model
    manager.switch_model = AsyncMock(return_value=model)
    return manager


def test_bench_engine_pipeline_3min_mock(
    benchmark, mock_model_manager: MagicMock, synthetic_song_3min: np.ndarray
) -> None:
    """InferencePipeline.run over a 3-minute song with a mock model."""
    pipeline = InferencePipeline(mock_model_manager)

    def _run_pipeline() -> None:
        _run(pipeline.run(synthetic_song_3min, 44100))

    benchmark(_run_pipeline)


def test_bench_engine_separate_3min_mock(
    benchmark, synthetic_song_3min: np.ndarray
) -> None:
    """DemucsSeparator.separate over a 3-minute song with mocked pipeline."""

    separator = DemucsSeparator(SeparationConfig())
    separator._preprocessor = MagicMock()
    separator._preprocessor.preprocess = AsyncMock(
        side_effect=lambda audio, sr, normalize: audio
    )
    separator._postprocessor = MagicMock()
    separator._postprocessor.postprocess = AsyncMock(
        side_effect=lambda audio, sr: audio
    )
    pipeline = MagicMock()
    pipeline.run = AsyncMock(
        side_effect=lambda audio, sr: {
            "vocals": audio,
            "other": audio,
        }
    )
    separator._pipeline = pipeline

    def _separate() -> None:
        _run(separator.separate(synthetic_song_3min, 44100))

    benchmark(_separate)
