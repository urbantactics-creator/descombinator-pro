"""Shared fixtures for the benchmark suite.

Fixtures generate deterministic synthetic audio in memory so benchmarks do
not depend on network access or large fixture files. Heavy fixtures are
cached per-session and marked ``slow`` where generation is expensive.
"""

import io
from collections.abc import Iterator
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

SAMPLE_RATE: int = 44_100


def _sine(duration: float, freq: float, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Generate a mono float32 sine wave of the given duration."""
    t = np.linspace(0.0, duration, int(sr * duration), endpoint=False)
    return (0.5 * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def _write_wav(path: Path, audio: np.ndarray, sr: int) -> None:
    """Write float32 audio to a WAV file via soundfile."""
    with sf.SoundFile(
        path, "w", samplerate=sr, channels=audio.ndim, subtype="PCM_16"
    ) as f:
        f.write(audio)


@pytest.fixture(scope="session")
def synthetic_song_3min() -> np.ndarray:
    """3-minute mono float32 song at 44.1 kHz (~7.9M samples, ~31.8 MB)."""
    t = np.linspace(0.0, 180.0, SAMPLE_RATE * 180, endpoint=False, dtype=np.float32)
    audio = (
        0.5 * np.sin(2 * np.pi * 220.0 * t)
        + 0.3 * np.sin(2 * np.pi * 440.0 * t)
        + 0.1 * np.sin(2 * np.pi * 880.0 * t)
    ).astype(np.float32)
    return audio


@pytest.fixture(scope="session")
def synthetic_stems() -> dict[str, np.ndarray]:
    """Dict of 1-minute synthetic stems (vocals/drums/bass/other)."""
    return {
        "vocals": _sine(60.0, 440.0),
        "drums": _sine(60.0, 220.0),
        "bass": _sine(60.0, 110.0),
        "other": _sine(60.0, 880.0),
    }


@pytest.fixture(scope="session")
def sample_audio_1min() -> np.ndarray:
    """1-minute mono float32 audio (~2.6M samples)."""
    return _sine(60.0, 330.0)


@pytest.fixture(scope="session")
def big_wav_100mb() -> Iterator[tuple[Path, int]]:
    """Write a ~100 MB WAV file to a temp dir (slow, session-scoped)."""
    import shutil
    import tempfile

    tmpdir = tempfile.mkdtemp(prefix="descombinator-bench-")
    path = Path(tmpdir) / "big_100mb.wav"
    # 100 MB of float32 ≈ 26.2M samples (about 9.9 minutes at 44.1 kHz).
    target_samples = int(100 * 1024 * 1024 / 4)
    audio = np.zeros(target_samples, dtype=np.float32)
    audio[::64] = 0.5
    _write_wav(path, audio, SAMPLE_RATE)
    yield path, SAMPLE_RATE
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture(scope="session")
def wav_bytes_1min() -> bytes:
    """In-memory 1-minute WAV file bytes for export benchmarks."""
    audio = _sine(60.0, 330.0)
    buf = io.BytesIO()
    sf.write(buf, audio, SAMPLE_RATE, format="WAV", subtype="PCM_16")
    return buf.getvalue()


@pytest.fixture
def bench_audio_numpy() -> np.ndarray:
    """Per-test float32 array reused by pure numpy benchmarks."""
    return _sine(1.0, 440.0)


@pytest.fixture
def bench_dummy_model(pytestconfig: pytest.Config) -> Iterator[object]:
    """Minimal async model double for pipeline benchmarks (no torch import)."""

    class _DummyModel:
        async def separate(self, audio: np.ndarray) -> dict[str, np.ndarray]:
            """Return a trivial stem copy, no-op separation."""
            data = audio.cpu().numpy() if hasattr(audio, "cpu") else audio
            return {"vocals": data, "other": data}

    yield _DummyModel()
