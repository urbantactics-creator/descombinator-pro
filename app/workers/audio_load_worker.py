"""Worker for loading audio data in a background thread."""

from __future__ import annotations

import asyncio
from pathlib import Path

from loguru import logger
from PySide6.QtCore import QObject, QRunnable, Signal

from engine.audio.loader import AudioLoader


class AudioLoadWorkerSignals(QObject):
    """Signals for AudioLoadWorker."""

    finished = Signal(object)  # tuple[np.ndarray, int]
    error = Signal(str)


class AudioLoadWorker(QRunnable):
    """Load audio file in a background thread for waveform display."""

    def __init__(self, file_path: Path, sample_rate: int = 44100) -> None:
        super().__init__()
        self._file_path = file_path
        self._sample_rate = sample_rate
        self.signals = AudioLoadWorkerSignals()

    def run(self) -> None:
        """Load audio file and emit result."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loader = AudioLoader()
            audio = loop.run_until_complete(
                loader.load(self._file_path, sr=self._sample_rate)
            )
            self.signals.finished.emit((audio, self._sample_rate))
        except Exception as e:
            logger.error(f"Failed to load audio: {e}")
            self.signals.error.emit(str(e))
        finally:
            loop.close()
