from __future__ import annotations
from typing import TYPE_CHECKING, Callable
import asyncio
import enum
from . import ai

if TYPE_CHECKING:
    from othello.game import BoardState
    from othello.bitboard import Position


class Color(enum.Enum):
    """
    Represents color of pieces.
    There can only be two colors.
    """
    BLACK = enum.auto()
    WHITE = enum.auto()


class Player:
    def __init__(self, color: Color):
        self._color = color
        self._loop = asyncio.get_running_loop()
        self._move = self._loop.create_future()

    @property
    def color(self):
        return self._color

    @property
    async def move(self) -> Position:
        """ The next move this player intends to make. """
        move = await self._move
        del self.move
        return move

    @move.setter
    def move(self, value: Position):
        def callback():
            if self._move.done():
                raise RuntimeError(f'Attempt to set {self} move but it has already been set')
            self._move.set_result(value)
        self._loop.call_soon_threadsafe(callback)

    @move.deleter
    def move(self):
        self._move = self._loop.create_future()

    def __repr__(self):
        return f'Player({self._color})'


class AIPlayer(Player):
    def __init__(self, color: Color, state: BoardState, strat: Callable[[BoardState], Position] = ai.random):
        super().__init__(color)
        self._strat = strat
        self._state = state

    @Player.move.getter  # pylint: disable=no-member
    async def move(self):  # pylint: disable=invalid-overridden-method
        return self._strat(self._state)
