"""Benchmarks for the audio loading and preprocessing pipeline."""

from __future__ import annotations

import asyncio
from pathlib import Path

import numpy as np
import pytest

from engine.audio.loader import AudioLoader
from engine.audio.postprocessor import AudioPostprocessor
from engine.audio.preprocessor import AudioPreprocessor

# Reuse a single event loop across benchmark iterations instead of creating
# one per call (asyncio.run). Loop creation is a measurable, noisy overhead
# on fast benchmarks and widens the median spread that the regression gate
# compares against.
_LOOP = asyncio.new_event_loop()


def _run(coro) -> object:
    return _LOOP.run_until_complete(coro)


@pytest.fixture(scope="session")
def loader() -> AudioLoader:
    return AudioLoader()


def test_bench_audio_load_1min_wav(
    benchmark, loader: AudioLoader, wav_bytes_1min: bytes
) -> None:
    """Load a 1-minute in-memory WAV file."""

    def _load() -> None:
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            tmp.write(wav_bytes_1min)
            tmp.flush()
            _run(loader.load(Path(tmp.name)))

    benchmark(_load)


def test_bench_audio_preprocess_3min(
    benchmark, synthetic_song_3min: np.ndarray
) -> None:
    """Preprocess a 3-minute song (DC removal + normalization + trim)."""
    preprocessor = AudioPreprocessor()

    def _preprocess() -> None:
        _run(preprocessor.preprocess(synthetic_song_3min, 44100, normalize=True))

    benchmark(_preprocess)


def test_bench_audio_postprocess_1min(
    benchmark, synthetic_stems: dict[str, np.ndarray]
) -> None:
    """Postprocess a 1-minute stem."""
    postprocessor = AudioPostprocessor()

    def _postprocess() -> None:
        _run(postprocessor.postprocess(synthetic_stems["vocals"], 44100))

    benchmark(_postprocess)
