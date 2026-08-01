"""Batch export for multiple audio stems."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path

import numpy as np
from loguru import logger

from engine.export.config import ExportConfig
from engine.export.errors import ExportError, WriteError
from engine.export.writer import ExportWriter


class BatchExporter:
    """Export multiple audio stems in batch with progress tracking."""

    def __init__(
        self,
        config: ExportConfig | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> None:
        self._config = config or ExportConfig()
        self._writer = ExportWriter(self._config)
        self._progress_callback = progress_callback

    async def export_all(
        self,
        stems: dict[str, np.ndarray],
        output_dir: Path,
        sample_rate: int = 44_100,
    ) -> list[Path]:
        """Export all stems to files in output_dir.

        Args:
            stems: Dict of stem_name -> numpy array.
            output_dir: Directory to write files into.
            sample_rate: Sample rate for output files.

        Returns:
            List of output file paths.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        results: list[Path] = []
        total = len(stems)

        for i, (stem_name, audio) in enumerate(stems.items(), 1):
            ext = self._config.format.value
            filename = f"{stem_name}.{ext}"
            output_path = output_dir / filename

            try:
                await self._writer.write_stem(
                    stem_name, audio, output_path, sample_rate
                )
                results.append(output_path)
                logger.info(f"Exported {stem_name} to {output_path}")
            except (WriteError, ExportError) as e:
                logger.error(f"Failed to export {stem_name}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error exporting {stem_name}: {e}")
                continue

            if self._progress_callback:
                self._progress_callback(i, total)

        return results

    async def export_parallel(
        self,
        stems: dict[str, np.ndarray],
        output_dir: Path,
        sample_rate: int = 44_100,
        max_concurrent: int = 4,
    ) -> list[Path]:
        """Export stems in parallel with controlled concurrency.

        Args:
            stems: Dict of stem_name -> numpy array.
            output_dir: Directory to write files into.
            sample_rate: Sample rate for output files.
            max_concurrent: Maximum number of concurrent exports.

        Returns:
            List of output file paths.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        semaphore = asyncio.Semaphore(max_concurrent)
        results: list[Path] = []
        total = len(stems)

        async def export_single(stem_name: str, audio: np.ndarray) -> Path | None:
            async with semaphore:
                ext = self._config.format.value
                filename = f"{stem_name}.{ext}"
                output_path = output_dir / filename

                try:
                    result = await self._writer.write_stem(
                        stem_name, audio, output_path, sample_rate
                    )
                    logger.info(f"Exported {stem_name} to {output_path}")
                    return result
                except (WriteError, ExportError) as e:
                    logger.error(f"Failed to export {stem_name}: {e}")
                    return None
                except Exception as e:
                    logger.error(f"Unexpected error exporting {stem_name}: {e}")
                    return None

        tasks = [export_single(name, audio) for name, audio in stems.items()]
        completed = await asyncio.gather(*tasks)

        for i, result in enumerate(completed, 1):
            if result:
                results.append(result)

            if self._progress_callback:
                self._progress_callback(i, total)

        return results
