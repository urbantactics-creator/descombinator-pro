"""Sync runner used by memory profiling.

Profiling via ``memory_profiler.memory_usage`` (or ``mprof run``) requires a
synchronous callable, so this module wraps the async pipeline in a plain
function. It builds a mock pipeline so no real model weights are needed.
"""

from __future__ import annotations

import numpy as np


def run_mock_pipeline() -> dict[str, np.ndarray]:
    """Run the mock separation pipeline synchronously over 3 minutes of audio.

    Returns the produced stems dict (so the profiler sees the peak allocations
    for input, activations, and output stems).
    """
    import asyncio
    from unittest.mock import AsyncMock, MagicMock

    from engine.demucs.config import SeparationConfig
    from engine.demucs.separator import DemucsSeparator

    mock_pipeline = MagicMock()
    mock_pipeline.run = AsyncMock(
        return_value={
            "vocals": np.zeros(44_100 * 180, dtype=np.float32),
            "other": np.zeros(44_100 * 180, dtype=np.float32),
        }
    )
    mock_preprocessor = MagicMock()
    mock_preprocessor.preprocess = AsyncMock(
        side_effect=lambda audio, sr, normalize=True: audio
    )
    mock_postprocessor = MagicMock()
    mock_postprocessor.postprocess = AsyncMock(side_effect=lambda stem, sr: stem)

    separator = DemucsSeparator(SeparationConfig())
    separator._pipeline = mock_pipeline
    separator._preprocessor = mock_preprocessor
    separator._postprocessor = mock_postprocessor

    sr = 44_100
    t = np.linspace(0.0, 180.0, sr * 180, endpoint=False, dtype=np.float32)
    audio = (0.5 * np.sin(2 * np.pi * 220.0 * t)).astype(np.float32)

    return asyncio.run(separator.separate(audio, sr))


def run_real_pipeline() -> dict[str, np.ndarray]:
    """Run the real separation pipeline (loads model weights).

    Intended for ``mprof run``/manual profiling of real memory peaks. Only
    invoked when the user passes ``--real``.
    """
    import asyncio

    from engine.demucs.config import SeparationConfig
    from engine.demucs.separator import DemucsSeparator

    async def _inner() -> dict[str, np.ndarray]:
        separator = DemucsSeparator(SeparationConfig())
        await separator.initialize()
        sr = 44_100
        t = np.linspace(0.0, 180.0, sr * 180, endpoint=False, dtype=np.float32)
        audio = (0.5 * np.sin(2 * np.pi * 220.0 * t)).astype(np.float32)
        return await separator.separate(audio, sr)

    return asyncio.run(_inner())


if __name__ == "__main__":
    import sys

    if "--real" in sys.argv:
        run_real_pipeline()
    else:
        run_mock_pipeline()
