"""Benchmarks for playback mixer and waveform decimation.

The mixer is measured via direct ``readData`` calls — no real ``QAudioSink``
is created (the known headless CI crash). ``PlaybackController``/persistence
are exercised through their public APIs without playing audio.
"""

from __future__ import annotations

import numpy as np
import pytest

from app.audio.mixer import AudioMixer
from app.controllers.playback_controller import PlaybackController
from app.widgets.waveform_view import decimate_waveform


@pytest.fixture
def mixer(synthetic_stems: dict[str, np.ndarray]) -> AudioMixer:
    """Mixer preloaded with the 4 synthetic stems."""
    from app.audio.mixer import MixerTrack

    m = AudioMixer()
    m.set_tracks(
        [
            MixerTrack(name=name, data=audio, sample_rate=44100)
            for name, audio in synthetic_stems.items()
        ]
    )
    return m


def test_bench_playback_readdata_1min(benchmark, mixer: AudioMixer) -> None:
    """Throughput of mixer.readData for a 1-minute mix buffer."""

    def _read() -> None:
        n = 44100 * 60
        remaining = n
        while remaining > 0:
            chunk = min(remaining, 4096)
            mixer.readData(chunk * mixer._bytes_per_frame)
            remaining -= chunk

    benchmark(_read)


def test_bench_playback_set_stems(
    benchmark, synthetic_stems: dict[str, np.ndarray]
) -> None:
    """PlaybackController.set_stems with persisted state."""
    ctrl = PlaybackController()

    def _set() -> None:
        ctrl.set_stems(synthetic_stems)

    benchmark(_set)


def test_bench_playback_set_track_volume(
    benchmark, synthetic_stems: dict[str, np.ndarray]
) -> None:
    """PlaybackController.set_track_volume on an existing stem."""
    ctrl = PlaybackController()
    ctrl.set_stems(synthetic_stems)

    def _volume() -> None:
        ctrl.set_track_volume("vocals", 0.75)

    benchmark(_volume)


def test_bench_waveform_decimate_100mb(
    benchmark, synthetic_song_3min: np.ndarray
) -> None:
    """Decimate a large waveform (3-min song proxy for the 100 MB target)."""

    def _decimate() -> None:
        decimate_waveform(synthetic_song_3min, sample_rate=44100)

    benchmark(_decimate)
