import logging
from othelloai import ui

_LOGGER = logging.getLogger('othello')

try:
    ui.loop()  # Blocked until application is closed or an error occurs
except KeyboardInterrupt:
    _LOGGER.info('Quitting application via KeyboardInterrupt...')
finally:
    logging.shutdown()
