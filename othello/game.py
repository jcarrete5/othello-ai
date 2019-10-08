import asyncio
import enum
from typing import Optional, List, Tuple
from collections import namedtuple

Position = namedtuple('Position', 'row, col', module=__name__)

class IllegalMoveError(Exception):
    """ Raised when an illegal move is attempted. """
    pass

class Color(enum.Enum):
    """ Represents color of pieces. """
    BLACK = enum.auto()
    WHITE = enum.auto()

class Player:
    def __init__(self, color: Color):
        assert color is not None
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
    def move(self, value: Position):
        if self._move.done():
            del self._move
        self._move.set_result(value)

    @move.deleter
    def move(self):
        loop = asyncio.get_running_loop()
        self._move = loop.create_future()

class Board():
    def __init__(self, size: int):
        self._size = size
        self._board: List[List[Optional[Color]]] = []
        for _ in range(size):
            self._board.append([None for _ in range(size)])
    
    @property
    def size(self) -> int:
        return self._size

    async def place(self, pos: Position, color: Color):
        """ Place a piece of color `color` at position `pos` """
        assert 0 <= pos.row < self._size
        assert 0 <= pos.col < self._size
        if self._board[pos.row][pos.col] is None:
            self._board[pos.row][pos.col] = color
            await self._update(pos, color)
        else:
            raise IllegalMoveError

    async def _update(self, pivot: Position, color: Color):
        # TODO This is garbage; use bit masks to represent the board
        def flip(row: int, col: int):
            if self._board[row][col] == Color.BLACK:
                self._board[row][col] = Color.WHITE
            elif self._board[row][col] == Color.WHITE:
                self._board[row][col] = Color.BLACK
        async def n():
            for row in range(pivot.row - 2, -1, -1):
                if self._board[row][pivot.col] == color:
                    for row in range(pivot.row - 1, row, -1):
                        flip(row, pivot.col)
                    break
        async def ne():
            for row in range(pivot.row - 2, -1, -1):
                if self._board[row][pivot.col] == color:
                    for row in range(pivot.row - 1, row, -1):
                        flip(row, pivot.col)
                    break
        async def e():
            for row in range(pivot.row - 2, -1, -1):
                if self._board[row][pivot.col] == color:
                    for row in range(pivot.row - 1, row, -1):
                        flip(row, pivot.col)
                    break
        async def se():
            for row in range(pivot.row - 2, -1, -1):
                if self._board[row][pivot.col] == color:
                    for row in range(pivot.row - 1, row, -1):
                        flip(row, pivot.col)
                    break
        async def s():
            for row in range(pivot.row - 2, -1, -1):
                if self._board[row][pivot.col] == color:
                    for row in range(pivot.row - 1, row, -1):
                        flip(row, pivot.col)
                    break
        async def sw():
            for row in range(pivot.row - 2, -1, -1):
                if self._board[row][pivot.col] == color:
                    for row in range(pivot.row - 1, row, -1):
                        flip(row, pivot.col)
                    break
        async def w():
            for row in range(pivot.row - 2, -1, -1):
                if self._board[row][pivot.col] == color:
                    for row in range(pivot.row - 1, row, -1):
                        flip(row, pivot.col)
                    break
        async def nw():
            for row in range(pivot.row - 2, -1, -1):
                if self._board[row][pivot.col] == color:
                    for row in range(pivot.row - 1, row, -1):
                        flip(row, pivot.col)
                    break
        await asyncio.gather(n, ne, e, se, s, sw, w, nw)
    
    def __repr__(self):
        def symbol_for(space: Optional[Color]):
            if space is None:
                return '-'
            elif space == Color.BLACK:
                return 'B'
            else:
                return 'W'
        res = []
        for row in self._board:
            res.append(f'[{" ".join(map(symbol_for, row))}]')
        return '\n'.join(res)

async def loop():
    # Game initialization
    user = Player(Color.BLACK)
    ai = Player(Color.WHITE)
    turn_player = user

    while True:
        move = await turn_player.move
        turn_player = user if turn_player is ai else ai