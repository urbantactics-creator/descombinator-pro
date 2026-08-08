"""Real separation benchmark with the actual htdemucs model.

Marked ``slow``: downloads/loads the real model and separates a 3-minute
synthetic song. Run manually or in CI with ``-m slow``. Target on CPU:
median < 30 s for a 3-minute song.
"""

import asyncio

import numpy as np
import pytest

from engine.demucs.config import ModelName, SeparationConfig
from engine.demucs.separator import DemucsSeparator


def _run(coro) -> object:
    return asyncio.run(coro)


@pytest.mark.slow
def test_bench_real_separation_3min(benchmark, synthetic_song_3min: np.ndarray) -> None:
    """Separate a 3-minute song with the real htdemucs model."""

    def _separate() -> None:
        separator = DemucsSeparator(SeparationConfig(model_name=ModelName.HTDEMUCS_FT))
        _run(separator.initialize())
        _run(separator.separate(synthetic_song_3min, 44100))

    benchmark(_separate)
