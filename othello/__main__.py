import asyncio
import logging
from othello import ui, game
from othello.player import Color, Player

async def main():
    user = Player(Color.BLACK)
    ai_player = Player(Color.WHITE)
    board = game.Board()
    await asyncio.gather(
        # ui.loop(),
        game.loop(user, ai_player, board))

try:
    asyncio.run(main(), debug=True)
finally:
    logging.shutdown()

###- Some Notes -###
# 3 kinds of players: NetworkPlayer, AIPlayer, ControlledPlayer
# Each player has their own overriden loop method that determines how their move will be set
# Remove the ai.loop method as that will not be how player moves are set
