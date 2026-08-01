"""Descombinator Pro — Audio source separation and processing engine."""

import os
import sys

from loguru import logger

from app.controllers.main_controller import MainController
from app.controllers.playback_controller import PlaybackController
from app.controllers.settings_controller import SettingsController
from app.ui.main_window import MainWindow


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


def main() -> None:
    """Entry point for the Descombinator Pro desktop application."""
    from PySide6.QtWidgets import QApplication

    configure_loguru()
    logger.info("Descombinator Pro starting...")

    app = QApplication(sys.argv)
    app.setApplicationName("Descombinator Pro")
    app.setOrganizationName("Descombinator")
    app.setApplicationVersion("0.1.0")

    settings_ctrl = SettingsController()
    settings_ctrl.load_settings()

    main_ctrl = MainController()
    playback_ctrl = PlaybackController()

    window = MainWindow(main_ctrl, playback_ctrl, settings_ctrl)
    window.show()

    logger.info("Application window displayed")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
