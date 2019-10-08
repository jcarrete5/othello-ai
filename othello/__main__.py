import os, asyncio, logging
import othello.ui as ui
import othello.game as game
logging.basicConfig(level=getattr(logging, os.getenv('LEVEL', ''), logging.WARNING))

async def main():
    asyncio.gather(ui.loop(), game.loop())

try:
    asyncio.run(main(), debug=True)
finally:
    logging.shutdown()