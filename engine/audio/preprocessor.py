"""Audio preprocessing: DC removal, normalization, silence trimming."""

from __future__ import annotations

import asyncio

import librosa
import numpy as np
from loguru import logger

from engine.audio.errors import PreprocessingError


class AudioPreprocessor:
    """Prepare audio for model inference."""

    async def remove_dc_offset(self, audio: np.ndarray) -> np.ndarray:
        """Remove DC offset by subtracting mean."""
        dc = float(np.mean(audio))
        if abs(dc) < 1e-10:
            logger.debug("DC offset negligible, returning copy")
            return audio.copy()
        result = (audio - dc).astype(np.float32)
        logger.debug(f"Removed DC offset: {dc:.6f}")
        return result

    async def normalize_peak(
        self,
        audio: np.ndarray,
        target_db: float = -1.0,
    ) -> np.ndarray:
        """Normalize peak to target dBFS. Handles silence gracefully."""
        peak = float(np.max(np.abs(audio)))
        if peak < 1e-10:
            logger.debug("Audio is silent, returning copy")
            return audio.copy()
        target_linear = 10 ** (target_db / 20)
        result = (audio * (target_linear / peak)).astype(np.float32)
        logger.debug(f"Normalized: peak {peak:.4f} → {target_linear:.4f}")
        return result

    async def clip_silence(
        self,
        audio: np.ndarray,
        sr: int,
        top_db: int = 30,
    ) -> np.ndarray:
        """Trim leading/trailing silence."""
        try:
            trimmed, _ = await asyncio.to_thread(
                librosa.effects.trim, audio, top_db=top_db
            )
            removed = len(audio) - len(trimmed)
            if removed > 0:
                logger.debug(f"Trimmed {removed / sr:.2f}s of silence")
            return trimmed
        except Exception as e:
            logger.error(f"Silence trimming failed: {e}")
            raise PreprocessingError(f"Cannot trim silence: {e}") from e

    async def preprocess(
        self,
        audio: np.ndarray,
        sr: int,
        normalize: bool = True,
    ) -> np.ndarray:
        """Full pipeline: DC removal → peak normalization."""
        result = await self.remove_dc_offset(audio)
        if normalize:
            result = await self.normalize_peak(result)
        return result
