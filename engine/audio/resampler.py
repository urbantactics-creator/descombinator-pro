"""Sample rate conversion and channel handling."""

import asyncio

import numpy as np
import resampy
from loguru import logger

from engine.audio.errors import ResampleError


class AudioResampler:
    """Resample audio and convert between mono/stereo."""

    DEFAULT_TARGET_SR: int = 44_100

    async def resample(
        self,
        audio: np.ndarray,
        orig_sr: int,
        target_sr: int = 44_100,
    ) -> np.ndarray:
        """Resample with kaiser_best quality. Skips if already at target."""
        return await asyncio.to_thread(self.resample_sync, audio, orig_sr, target_sr)

    def resample_sync(
        self,
        audio: np.ndarray,
        orig_sr: int,
        target_sr: int = 44_100,
    ) -> np.ndarray:
        """Synchronous resample for use inside worker threads.

        Keeps the existing logging and error contract of ``resample`` while
        remaining callable from code already running in a thread.

        Multi-channel input must be channels-first ``(C, N)`` so that
        resampling acts on the samples axis (``axis=-1``).
        """
        if orig_sr == target_sr:
            logger.debug(f"Already at {target_sr} Hz, returning copy")
            return audio.copy()

        try:
            resampled = resampy.resample(
                audio, orig_sr, target_sr, filter="kaiser_best", axis=-1
            )
            duration = len(resampled) / target_sr
            logger.info(
                f"Resampled {orig_sr}→{target_sr} Hz: "
                f"samples={len(resampled)}, duration={duration:.2f}s"
            )
            return resampled
        except Exception as e:
            logger.error(f"Resample failed {orig_sr}→{target_sr}: {e}")
            raise ResampleError(f"Cannot resample {orig_sr}→{target_sr}: {e}") from e

    async def to_mono(self, audio: np.ndarray) -> np.ndarray:
        """Convert stereo to mono by averaging channels. No-op if already mono.

        Expects channels-first ``(C, N)`` input (axis 0 = channels), the same
        convention produced by ``AudioLoader`` and librosa. (Regression A5.)
        """
        if audio.ndim == 1:
            return audio.copy()
        mono = np.mean(audio, axis=0).astype(np.float32)
        logger.debug(f"Converted stereo→mono: shape {audio.shape} → {mono.shape}")
        return mono

    async def ensure_mono(
        self,
        audio: np.ndarray,
        sr: int,
        target_sr: int = 44_100,
    ) -> np.ndarray:
        """Combined: mono conversion + resample."""
        mono = await self.to_mono(audio)
        return await self.resample(mono, sr, target_sr)
