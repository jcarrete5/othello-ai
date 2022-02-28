"""Program script entry points."""

import logging
import os

from . import gui
from .args import get_args

_logger = logging.getLogger(__name__)


def setup_logging():
    """Initialize logging for entry points."""
    logging.basicConfig(
        style="{",
        format="[{name}:{levelname}] - {threadName} - In {funcName}: {message}",
        level=getattr(logging, os.getenv("LOG", ""), logging.WARNING),
    )


def start_gui():
    """Entry point to start the GUI."""
    setup_logging()
    get_args().parse_args()
    try:
        gui.loop()  # Blocked until application is closed or an error occurs
    except KeyboardInterrupt:
        print("Quitting application via KeyboardInterrupt...")
    finally:
        logging.shutdown()
