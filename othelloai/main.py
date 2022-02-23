"""Program script entry points."""

import logging

from othelloai import ui

_logger = logging.getLogger("othello")


def start_ui():
    try:
        ui.loop()  # Blocked until application is closed or an error occurs
    except KeyboardInterrupt:
        _logger.info("Quitting application via KeyboardInterrupt...")
    finally:
        logging.shutdown()
