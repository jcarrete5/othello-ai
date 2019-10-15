import os, asyncio, logging
import othello.ui as ui
import othello.game as game

logging.basicConfig(style='{',
                    format='[{name}:{levelname}] In {funcName}: {message}',
                    level=getattr(logging, os.getenv('LOG', ''), logging.WARNING))
logger = logging.getLogger(__name__)

async def main():
    user = game.Player(game.Color.BLACK)
    await asyncio.gather(
        ui.loop(),
        game.loop(user))

try:
    asyncio.run(main(), debug=True)
finally:
    logging.shutdown()