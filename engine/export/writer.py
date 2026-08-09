"""Export writer for separated audio stems."""

import asyncio
import subprocess
import tempfile
from contextlib import suppress
from pathlib import Path

import numpy as np
import soundfile as sf
from loguru import logger

from engine.export.config import ExportConfig
from engine.export.errors import UnsupportedFormatError, WriteError
from engine.export.metadata import MetadataEmbedder


class ExportWriter:
    """Write separated audio stems to disk."""

    def __init__(self, config: ExportConfig | None = None) -> None:
        self._config = config or ExportConfig()
        self._metadata_embedder = MetadataEmbedder()

    async def write(
        self,
        stems: dict[str, np.ndarray],
        output_dir: Path,
        sample_rate: int = 44_100,
    ) -> dict[str, Path]:
        """Write all stems to files in output_dir.

        Args:
            stems: Dict of stem_name -> numpy array.
            output_dir: Directory to write files into.
            sample_rate: Sample rate for output files.

        Returns:
            Dict of stem_name -> output file path.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        results: dict[str, Path] = {}

        for stem_name, audio in stems.items():
            ext = self._config.format.value
            filename = f"{stem_name}.{ext}"
            output_path = output_dir / filename

            await self._write_stem(audio, output_path, sample_rate)
            results[stem_name] = output_path
            logger.info(f"Exported {stem_name} to {output_path}")

        return results

    async def write_stem(
        self,
        stem_name: str,
        audio: np.ndarray,
        output_path: Path,
        sample_rate: int = 44_100,
    ) -> Path:
        """Write a single stem to a specific path."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        await self._write_stem(audio, output_path, sample_rate)
        return output_path

    async def write_with_metadata(
        self,
        stem_name: str,
        audio: np.ndarray,
        output_path: Path,
        sample_rate: int = 44_100,
    ) -> Path:
        """Write a single stem with metadata to a specific path."""
        await self._write_stem(audio, output_path, sample_rate)

        if self._config.metadata:
            metadata_dict = {
                "title": self._config.metadata.title,
                "artist": self._config.metadata.artist,
                "album": self._config.metadata.album,
                "genre": self._config.metadata.genre,
            }
            await self._metadata_embedder.embed(output_path, metadata_dict)

        return output_path

    async def _write_stem(
        self,
        audio: np.ndarray,
        path: Path,
        sample_rate: int,
    ) -> None:
        """Write a single stem to disk."""
        try:
            audio = np.clip(audio, -1.0, 1.0).astype(np.float32)

            # Stems arrive channels-first (C, N) from the inference pipeline,
            # but soundfile and lameenc expect frames-first (N, C) interleaved
            # audio. Normalize the layout here so every format writer below
            # receives a frames-first buffer.
            if audio.ndim == 2:
                audio = np.ascontiguousarray(audio.T)

            suffix = path.suffix.lower()
            if suffix == ".wav":
                await self._write_wav(audio, path, sample_rate)
            elif suffix == ".flac":
                await self._write_flac(audio, path, sample_rate)
            elif suffix == ".mp3":
                await self._write_mp3(audio, path, sample_rate)
            elif suffix in (".m4a", ".mp4"):
                await self._write_m4a(audio, path, sample_rate)
            else:
                raise UnsupportedFormatError(f"Unsupported format: {suffix}")

        except WriteError, UnsupportedFormatError:
            raise
        except Exception as e:
            logger.error(f"Failed to write {path}: {e}")
            raise WriteError(f"Cannot write {path.name}: {e}") from e

    async def _write_wav(
        self,
        audio: np.ndarray,
        path: Path,
        sample_rate: int,
    ) -> None:
        """Write WAV file."""
        await asyncio.to_thread(sf.write, str(path), audio, sample_rate)
        logger.debug(f"Wrote WAV: {path.name}")

    async def _write_flac(
        self,
        audio: np.ndarray,
        path: Path,
        sample_rate: int,
    ) -> None:
        """Write FLAC file."""
        await asyncio.to_thread(sf.write, str(path), audio, sample_rate)
        logger.debug(f"Wrote FLAC: {path.name}")

    async def _write_mp3(
        self,
        audio: np.ndarray,
        path: Path,
        sample_rate: int,
    ) -> None:
        """Write MP3 file using lameenc."""
        try:
            import lameenc
        except ImportError as err:
            raise WriteError(
                "lameenc not installed. Install with: pip install lameenc"
            ) from err

        encoder = lameenc.Encoder()
        encoder.set_bit_rate(self._config.bitrate // 1000)
        encoder.set_channels(1 if audio.ndim == 1 else audio.shape[1])
        encoder.set_in_sample_rate(sample_rate)
        encoder.set_out_sample_rate(sample_rate)
        encoder.set_quality(2)

        audio_int16 = (audio * 32767).astype(np.int16)

        with open(str(path), "wb") as f:
            f.write(encoder.encode(audio_int16.tobytes()))
            f.write(encoder.flush())

        logger.debug(f"Wrote MP3: {path.name}")

    async def _write_m4a(
        self,
        audio: np.ndarray,
        path: Path,
        sample_rate: int,
    ) -> None:
        """Write M4A file using ffmpeg."""

        def _write_sync() -> None:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_path = temp_wav.name
            try:
                sf.write(str(temp_path), audio, sample_rate)

                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(temp_path),
                    "-c:a",
                    "aac",
                    "-b:a",
                    f"{self._config.bitrate // 1000}k",
                    "-ar",
                    str(sample_rate),
                    str(path),
                ]

                if path.exists():
                    logger.info(f"Overwriting existing file: {path.name}")
                subprocess.run(
                    cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
                )
                logger.debug(f"Wrote M4A: {path.name}")
            except subprocess.CalledProcessError as e:
                raise WriteError(f"FFmpeg failed to write M4A: {e}") from e
            finally:
                with suppress(OSError):
                    Path(temp_path).unlink()

        try:
            await asyncio.to_thread(_write_sync)
        except WriteError:
            raise
        except Exception as e:
            logger.error(f"Failed to write M4A {path}: {e}")
            raise WriteError(f"Cannot write {path.name}: {e}") from e
