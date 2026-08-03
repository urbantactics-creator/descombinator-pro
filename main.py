"""Descombinator Pro — Audio source separation and processing engine."""

from __future__ import annotations

import multiprocessing
import os
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def get_resource_path(relative: str) -> Path:
    """Resolve a resource path for both frozen and development modes.

    When running as a PyInstaller bundle, ``sys._MEIPASS`` is the temp
    directory where bundled data is extracted.  In development mode the
    project root is used instead.
    """
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).parent
    return base / relative


def _app_version() -> str:
    """Return the installed package version or fall back to 0.1.0."""
    try:
        return version("descombinator")
    except PackageNotFoundError:
        return "0.1.0"


def configure_loguru() -> None:
    """Configure loguru from environment variables."""
    from loguru import logger

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
    multiprocessing.freeze_support()

    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    from app.controllers.main_controller import MainController
    from app.controllers.playback_controller import PlaybackController
    from app.controllers.settings_controller import SettingsController
    from app.ui.main_window import MainWindow

    configure_loguru()

    from loguru import logger

    logger.info("Descombinator Pro starting...")

    app = QApplication(sys.argv)
    app.setApplicationName("Descombinator Pro")
    app.setOrganizationName("Descombinator")
    app.setApplicationVersion(_app_version())

    icon_path = get_resource_path("assets/icons/icon.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

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
