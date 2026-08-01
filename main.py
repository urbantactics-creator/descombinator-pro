"""Descombinator Pro — Audio source separation and processing engine."""

import asyncio
import os
import sys

from loguru import logger


def configure_loguru() -> None:
    """Configure loguru from environment variables."""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE")

    logger.remove()

    logger.add(
        sys.stderr,
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "{message}"
        ),
    )

    if log_file:
        logger.add(
            log_file,
            rotation="10 MB",
            retention="7 days",
            level="DEBUG",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
                "{name}:{function}:{line} | {message}"
            ),
        )


async def main() -> None:
    """Entry point for the descombinator audio processing engine."""
    configure_loguru()
    logger.info("Descombinator engine starting...")

    # TODO(phase-2): implement pipeline
    # from app.services.pipeline import PipelineService
    # from engine.audio.loader import AudioLoader
    # from engine.demucs.separator import DemucsSeparator
    # from engine.export.writer import ExportWriter
    #
    # loader = AudioLoader()
    # separator = DemucsSeparator()
    # writer = ExportWriter()
    #
    # pipeline = PipelineService(loader, separator, writer)
    # await pipeline.run()

    logger.info("Descombinator engine finished.")


if __name__ == "__main__":
    asyncio.run(main())
