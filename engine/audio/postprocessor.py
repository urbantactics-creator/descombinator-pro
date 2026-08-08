"""Audio postprocessing: peak limiting, fades, crossfade."""

import numpy as np
from loguru import logger


class AudioPostprocessor:
    """Clean up audio after model inference."""

    async def peak_limit(
        self,
        audio: np.ndarray,
        ceiling_db: float = -0.3,
    ) -> np.ndarray:
        """Hard-clip peaks above ceiling to prevent clipping."""
        ceiling = 10 ** (ceiling_db / 20)
        clipped_count = int(np.sum(np.abs(audio) > ceiling))
        result = np.clip(audio, -ceiling, ceiling).astype(np.float32)
        if clipped_count > 0:
            logger.debug(
                f"Peak limited: {clipped_count} samples clipped at {ceiling_db} dB"
            )
        return result

    async def fade_in_out(
        self,
        audio: np.ndarray,
        sr: int,
        fade_duration: float = 0.02,
    ) -> np.ndarray:
        """Apply linear fade-in and fade-out to prevent clicks."""
        fade_samples = int(sr * fade_duration)
        if fade_samples == 0 or len(audio) < 2 * fade_samples:
            return audio.copy()

        result = audio.copy()
        ramp_in = np.linspace(0.0, 1.0, fade_samples, dtype=np.float32)
        result[:fade_samples] *= ramp_in
        ramp_out = np.linspace(1.0, 0.0, fade_samples, dtype=np.float32)
        result[-fade_samples:] *= ramp_out
        return result

    async def crossfade(
        self,
        audio_a: np.ndarray,
        audio_b: np.ndarray,
        sr: int,
        overlap: float = 0.01,
    ) -> np.ndarray:
        """Crossfade two arrays. Handles different lengths gracefully."""
        overlap_samples = int(sr * overlap)
        if overlap_samples == 0:
            return np.concatenate([audio_a, audio_b])

        overlap_samples = min(overlap_samples, len(audio_a), len(audio_b))
        if overlap_samples == 0:
            return np.concatenate([audio_a, audio_b])

        fade_out = np.linspace(1.0, 0.0, overlap_samples, dtype=np.float32)
        fade_in = np.linspace(0.0, 1.0, overlap_samples, dtype=np.float32)

        result = np.empty(
            len(audio_a) + len(audio_b) - overlap_samples, dtype=np.float32
        )
        result[: len(audio_a) - overlap_samples] = audio_a[:-overlap_samples]
        result[len(audio_a) - overlap_samples : len(audio_a)] = (
            audio_a[-overlap_samples:] * fade_out + audio_b[:overlap_samples] * fade_in
        )
        result[len(audio_a) :] = audio_b[overlap_samples:]
        return result

    async def postprocess(
        self,
        audio: np.ndarray,
        sr: int,
        fade: bool = True,
        limit: bool = True,
    ) -> np.ndarray:
        """Full pipeline: fade → peak limit."""
        result = audio
        if fade:
            result = await self.fade_in_out(result, sr)
        if limit:
            result = await self.peak_limit(result)
        return result
