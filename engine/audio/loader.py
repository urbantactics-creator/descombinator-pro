"""Audio file loading with format validation and fast paths.

The loader prefers the cheapest decode path per format:

- WAV PCM (16/24/32-bit int, 32-bit float): header parsed and data
  ``np.memmap``-ed directly, avoiding a full library decode.
- Other WAV / FLAC / AIFF: ``soundfile``.
- MP3 / M4A / OGG: ``librosa``.

Every path returns float32 audio in [-1, 1]. ``librosa`` is imported
function-local so it is not pulled into the process at import time.
"""

from __future__ import annotations

import asyncio
import struct
from pathlib import Path
from typing import Any, ClassVar

import numpy as np
from loguru import logger

from engine.audio.errors import AudioFileNotFoundError, AudioFormatError, AudioLoadError
from engine.audio.resampler import AudioResampler


class AudioLoader:
    """Load audio files into numpy arrays."""

    SUPPORTED_FORMATS: ClassVar[frozenset[str]] = frozenset(
        {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".aiff"}
    )

    _SF_FORMATS: ClassVar[frozenset[str]] = frozenset({".wav", ".flac", ".aiff"})

    def __init__(self) -> None:
        """Initialize the loader with a shared resampler."""
        self._resampler = AudioResampler()

    def validate_exists(self, path: Path) -> None:
        """Raise if file does not exist."""
        if not path.exists():
            raise AudioFileNotFoundError(f"File not found: {path}")

    def validate_format(self, path: Path) -> None:
        """Raise if format is not supported."""
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise AudioFormatError(
                f"Unsupported format '{path.suffix}' for {path.name}. "
                f"Supported: {', '.join(sorted(self.SUPPORTED_FORMATS))}"
            )

    async def load(
        self,
        path: Path,
        sr: int = 44_100,
        mono: bool = True,
    ) -> np.ndarray:
        """Load audio file into float32 array normalized to [-1, 1]."""
        self.validate_exists(path)
        self.validate_format(path)
        try:
            audio = await self._load_decoded(path, sr, mono)
            duration = len(audio) / sr
            logger.info(
                f"Loaded {path.name}: shape={audio.shape}, sr={sr}, "
                f"duration={duration:.2f}s"
            )
            return audio
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
            raise AudioLoadError(f"Cannot load {path.name}: {e}") from e

    async def _load_decoded(
        self,
        path: Path,
        sr: int,
        mono: bool,
    ) -> np.ndarray:
        """Pick the cheapest decode path for the file format."""
        suffix = path.suffix.lower()

        if suffix == ".wav":
            wav = await asyncio.to_thread(self._load_wav_pcm, path, sr, mono)
            if wav is not None:
                return wav

        if suffix in self._SF_FORMATS:
            try:
                return await self._load_soundfile(path, sr, mono)
            except Exception as e:
                logger.warning(
                    f"soundfile failed for {path.name} ({e}); falling back to librosa"
                )

        return await self._load_librosa(path, sr, mono)

    def _parse_wav_header(self, path: Path) -> dict[str, Any] | None:
        """Parse a RIFF/WAVE header.

        Returns a dict with fmt metadata and the byte offset of the ``data``
        chunk, or ``None`` if the file is not a standard PCM WAV.
        """
        try:
            with open(path, "rb") as f:
                riff = f.read(12)
                if len(riff) < 12 or riff[:4] != b"RIFF" or riff[8:12] != b"WAVE":
                    return None
                audio_format: int | None = None
                channels: int | None = None
                sample_rate: int | None = None
                bits_per_sample: int | None = None
                data_offset: int | None = None
                data_size: int | None = None

                while True:
                    chunk_header = f.read(8)
                    if len(chunk_header) < 8:
                        break
                    chunk_id = chunk_header[:4]
                    (chunk_size,) = struct.unpack("<I", chunk_header[4:8])
                    if chunk_id == b"fmt ":
                        fmt = f.read(16)
                        if len(fmt) < 16:
                            return None
                        (
                            audio_format,
                            channels,
                            sample_rate,
                            _byte_rate,
                            _block_align,
                            bits_per_sample,
                        ) = struct.unpack("<HHIIHH", fmt[:16])
                        if chunk_size > 16:
                            f.seek(chunk_size - 16, 1)
                    elif chunk_id == b"data":
                        data_offset = f.tell()
                        data_size = chunk_size
                        break
                    else:
                        f.seek(chunk_size, 1)

                if (
                    audio_format is None
                    or channels is None
                    or sample_rate is None
                    or bits_per_sample is None
                    or data_offset is None
                    or data_size is None
                ):
                    return None
                return {
                    "audio_format": audio_format,
                    "channels": channels,
                    "sample_rate": sample_rate,
                    "bits_per_sample": bits_per_sample,
                    "data_offset": data_offset,
                    "data_size": data_size,
                }
        except (OSError, ValueError, struct.error):
            return None

    def _load_wav_pcm(
        self,
        path: Path,
        sr: int,
        mono: bool,
    ) -> np.ndarray | None:
        """Load standard PCM WAV via memory-mapped data region.

        Returns float32 mono/stereo audio or ``None`` to signal fallback.
        """
        info = self._parse_wav_header(path)
        if info is None:
            return None

        channels = int(info["channels"])
        bits = int(info["bits_per_sample"])
        data_offset = int(info["data_offset"])
        data_size = int(info["data_size"])
        audio_format = int(info["audio_format"])

        if audio_format == 1:  # PCM integer
            if bits == 16:
                int_dtype: np.dtype | None = np.dtype("<i2")
            elif bits == 32:
                int_dtype = np.dtype("<i4")
            elif bits == 24:
                return self._load_wav_pcm24(path, info, sr, mono)
            else:
                return None
            assert int_dtype is not None
            bytes_per = int_dtype.itemsize
            n_frames = data_size // (channels * bytes_per)
            if n_frames <= 0:
                return None
            view = np.memmap(
                path,
                dtype=int_dtype,
                mode="r",
                offset=data_offset,
                shape=(n_frames, channels),
            )
            scale = float(2 ** (bits - 1))
            audio: np.ndarray = view.astype(np.float32) / scale
        elif audio_format == 3 and bits == 32:  # IEEE float
            bytes_per = 4
            n_frames = data_size // (channels * bytes_per)
            if n_frames <= 0:
                return None
            view = np.memmap(
                path,
                dtype="<f4",
                mode="r",
                offset=data_offset,
                shape=(n_frames, channels),
            )
            audio = view.copy()
        else:
            return None

        native_sr = int(info["sample_rate"])
        return self._finalize(audio, native_sr, sr, mono)

    def _load_wav_pcm24(
        self,
        path: Path,
        info: dict[str, Any],
        sr: int,
        mono: bool,
    ) -> np.ndarray | None:
        """Load 24-bit PCM (3 bytes/sample) by decoding byte triplets."""
        data_offset = int(info["data_offset"])
        data_size = int(info["data_size"])
        channels = int(info["channels"])
        frames = data_size // (channels * 3)
        if frames <= 0:
            return None
        raw = np.memmap(
            path, dtype=np.uint8, mode="r", offset=data_offset, shape=data_size
        )
        n = frames * channels
        b0 = raw[: n * 3 : 3].astype(np.int32)
        b1 = raw[1 : n * 3 : 3].astype(np.int32)
        b2 = raw[2 : n * 3 : 3].astype(np.int32)
        value = (b2 << 16) | (b1 << 8) | b0
        value = np.where(value >= 0x800000, value - 0x1000000, value)
        audio = value.reshape(frames, channels).astype(np.float32) / 8388608.0
        return self._finalize(audio, int(info["sample_rate"]), sr, mono)

    def _finalize(
        self,
        audio: np.ndarray,
        native_sr: int,
        sr: int,
        mono: bool,
    ) -> np.ndarray:
        """Convert decoded frames to the requested channel layout and rate."""
        if audio.ndim == 1:
            audio = audio.reshape(-1, 1)
        if mono:
            if audio.shape[1] == 1:
                audio = audio[:, 0]
            else:
                audio = np.mean(audio, axis=1).astype(np.float32)
        else:
            audio = audio.T
        if native_sr != sr:
            audio = self._resampler.resample_sync(audio, native_sr, sr)
        return audio

    async def _load_soundfile(
        self,
        path: Path,
        sr: int,
        mono: bool,
    ) -> np.ndarray:
        """Load WAV (non-PCM), FLAC and AIFF via soundfile."""
        import soundfile as sf

        def _read() -> np.ndarray:
            data, native_sr = sf.read(path, dtype="float32", always_2d=True)
            return self._finalize(data, int(native_sr), sr, mono)

        return await asyncio.to_thread(_read)

    async def _load_librosa(
        self,
        path: Path,
        sr: int,
        mono: bool,
    ) -> np.ndarray:
        """Fallback loader for MP3/M4A/OGG and files soundfile cannot read."""
        import librosa

        audio, _ = await asyncio.to_thread(librosa.load, path, sr=sr, mono=mono)
        return audio
