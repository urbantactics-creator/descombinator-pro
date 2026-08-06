"""Export service for saving separated audio stems."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from loguru import logger

from engine.export.config import ExportConfig
from engine.export.writer import ExportWriter


class ExportService:
    """Service for exporting separated audio stems to files."""

    def __init__(self, config: ExportConfig | None = None) -> None:
        self._config = config or ExportConfig()
        self._writer = ExportWriter(self._config)

    async def export_stems(
        self,
        stems: dict[str, np.ndarray],
        output_dir: Path,
    ) -> dict[str, Path]:
        """Export audio stems to files.

        Args:
            stems: Dictionary mapping stem names to audio data as numpy arrays
            output_dir: Directory to save exported files

        Returns:
            Dictionary mapping stem names to output file paths
        """
        logger.info(f"Exporting {len(stems)} stems to {output_dir}")

        # Use the ExportWriter to write the stems
        result = await self._writer.write(stems, output_dir)

        return result

    def update_config(self, config: ExportConfig) -> None:
        """Update the export configuration."""
        self._config = config
        self._writer = ExportWriter(self._config)
