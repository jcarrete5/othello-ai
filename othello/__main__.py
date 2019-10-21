import logging
import threading
import asyncio
from othello import ui, game

_LOGGER = logging.getLogger('othello')

INTERRUPT_EVENT = threading.Event()
BOARD_STATE = game.BoardState(init_white=0x0000001008000000, init_black=0x0000000810000000)
GAME_THREAD = threading.Thread(
    target=lambda: asyncio.run(game.loop(BOARD_STATE), debug=True),
    name='game_thread')
GAME_THREAD.start()

try:
    ui.loop(BOARD_STATE)  # Blocked until application is closed or an error occurs
except KeyboardInterrupt:
    _LOGGER.info('Quitting application via KeyboardInterrupt...')
finally:
    game.quit_()
    GAME_THREAD.join()
    logging.shutdown()

###- Some Notes -###
# 3 kinds of players: NetworkPlayer, AIPlayer, ControlledPlayer
# Each player has their own overriden loop method that determines how their move will be set
# Remove the ai.loop method as that will not be how player moves are set
