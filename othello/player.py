import asyncio
import enum
from othello import bitboard as bb


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
        loop = asyncio.get_running_loop()
        self._move = loop.create_future()

    @property
    def color(self):
        return self._color

    @property
    async def move(self):
        """ The next move this player intends to make. """
        return await self._move

    @move.setter
    def move(self, value: bb.Position):
        if self._move.done():
            del self._move
        self._move.set_result(value)

    @move.deleter
    def move(self):
        loop = asyncio.get_running_loop()
        self._move = loop.create_future()

    def __repr__(self):
        return f'Player({self._color})'
