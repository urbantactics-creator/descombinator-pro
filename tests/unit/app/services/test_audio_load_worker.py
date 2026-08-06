"""Tests for the AudioLoadWorker."""

from __future__ import annotations

from app.workers.audio_load_worker import AudioLoadWorker


class TestAudioLoadWorkerInit:
    """Tests for AudioLoadWorker initialization."""

    def test_creates_with_file_path(self, tmp_path) -> None:
        """Worker can be created with a file path."""
        wav_file = tmp_path / "test.wav"
        wav_file.write_bytes(b"\x00" * 44)
        worker = AudioLoadWorker(wav_file)
        assert worker._file_path == wav_file
        assert worker._sample_rate == 44100

    def test_custom_sample_rate(self, tmp_path) -> None:
        """Worker accepts custom sample rate."""
        wav_file = tmp_path / "test.wav"
        wav_file.write_bytes(b"\x00" * 44)
        worker = AudioLoadWorker(wav_file, sample_rate=22050)
        assert worker._sample_rate == 22050


class TestAudioLoadWorkerSignals:
    """Tests for worker signal objects."""

    def test_signals_has_finished(self) -> None:
        """Signals object has finished signal."""
        from app.workers.audio_load_worker import AudioLoadWorkerSignals

        signals = AudioLoadWorkerSignals()
        assert hasattr(signals, "finished")

    def test_signals_has_error(self) -> None:
        """Signals object has error signal."""
        from app.workers.audio_load_worker import AudioLoadWorkerSignals

        signals = AudioLoadWorkerSignals()
        assert hasattr(signals, "error")
