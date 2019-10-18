import asyncio
import random as rand
from typing import Callable
from othello.player import Player
import othello.game as game
import othello.bitboard as bb

Strategy = Callable[[int], bb.Position]

turn = asyncio.Event()

async def loop(strategy: Strategy, player: Player, board: game.Board):
    while True:
        await turn.wait()
        player.move = strategy()

def random(bb: 'Board') -> bb.Position:
    pass