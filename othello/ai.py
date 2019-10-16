import asyncio
import random as rand
from typing import Callable
import othello.game as game
import othello.bitboard as bb

Strategy = Callable[[bb.Bitboard], bb.Position]

turn = asyncio.Event()

async def loop(strategy: Strategy, player: game.Player, board: game.Board):
    while True:
        await turn.wait()
        player.move = strategy()

def random(bb: game.Board) -> bb.Position:
    pass