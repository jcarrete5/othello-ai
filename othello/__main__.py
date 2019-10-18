import os
import asyncio
import logging
import othello.ui as ui
import othello.game as game
import othello.ai as ai
from othello.player import Color, Player

logging.basicConfig(style='{',
                    format='[{name}:{levelname}] In {funcName}: {message}',
                    level=getattr(logging, os.getenv('LOG', ''), logging.WARNING))
logger = logging.getLogger(__name__)

async def main():
    user = Player(Color.BLACK)
    ai_player = Player(Color.WHITE)
    board = game.Board()
    await asyncio.gather(
        # ui.loop(),
        ai.loop(ai.random, ai_player, board),
        game.loop(user, ai_player, board))

try:
    asyncio.run(main(), debug=True)
finally:
    logging.shutdown()

###- Some Notes -###
# 3 kinds of players: NetworkPlayer, AIPlayer, ControlledPlayer
# Each player has their own overriden loop method that determines how their move will be set
# Remove the ai.loop method as that will not be how player moves are set