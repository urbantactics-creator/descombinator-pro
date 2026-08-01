"""Descombinator - Audio source separation and processing engine."""

import asyncio
import logging
import sys

from app.services.pipeline import PipelineService
from engine.audio.loader import AudioLoader
from engine.demucs.separator import DemucsSeparator
from engine.export.writer import ExportWriter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Entry point for the descombinator audio processing engine."""
    logger.info("Descombinator engine starting...")

    loader = AudioLoader()
    separator = DemucsSeparator()
    writer = ExportWriter()

    pipeline = PipelineService(loader, separator, writer)
    await pipeline.run()

    logger.info("Descombinator engine finished.")


if __name__ == "__main__":
    asyncio.run(main())
