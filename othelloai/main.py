"""Program script entry points."""

import logging
import os

from . import gui

_logger = logging.getLogger(__name__)


def setup_logging():
    """Setup logging for entry points."""

    logging.basicConfig(
        style="{",
        format="[{name}:{levelname}] - {threadName} - In {funcName}: {message}",
        level=getattr(logging, os.getenv("LOG", ""), logging.WARNING),
    )


def start_gui():
    """Entry point to start the GUI."""

    setup_logging()
    try:
        gui.loop()  # Blocked until application is closed or an error occurs
    except KeyboardInterrupt:
        _logger.warning("Quitting application via KeyboardInterrupt...")
    finally:
        logging.shutdown()
