import asyncio
import enum
import logging
from typing import Optional, List, Tuple
import othello.ai as ai
import othello.bitboard as bb

_logger = logging.getLogger(__name__)

class IllegalMoveError(Exception):
    """ Raised when an illegal move is attempted. """
    pass

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
        return f'Player: {self._color}'

class Board():
    def __init__(self):
        self._white = 0x0000001008000000  # White piece bitboard
        self._black = 0x0000000810000000  # Black piece bitboard

    def empty_cells(self) -> bb.Bitboard:
        return bb.not_(self._white | self._black)

    def valid_moves_for(self, color: Color) -> List[bb.Position]:
        if color is Color.BLACK:
            my_pieces = self._black
            foe_pieces = self._white
        else:
            my_pieces = self._white
            foe_pieces = self._black
        moves_bb = 0x0
        for dir_ in bb.directions:
            candidates = foe_pieces & bb.shift(my_pieces, dir_)
            while candidates != 0:
                shifted = bb.shift(candidates, dir_)
                moves_bb |= self.empty_cells() & shifted
                candidates = foe_pieces & shifted
        return bb.to_list(moves_bb)
    
    def place(self, color: Color, pos: bb.Position):
        """ Place a piece of color `color` at position `pos` """
        assert 0 <= pos.row < 8
        assert 0 <= pos.col < 8
        pos_mask = bb.pos_mask(*pos)
        if color is Color.BLACK:
            self._black |= pos_mask
        else:
            self._white |= pos_mask
        self._capture(color, pos)
    
    def _capture(self, color: Color, pos: bb.Position):
        """ Find pieces that should be captured by playing `color` at `pos` and capture those pieces """
        my_pieces = self._white if color is Color.WHITE else self._black
        class State:
            def __init__(self, dir_, init_bb=0x0):
                self.bb = init_bb
                self.dir = dir_
                self.capped = False
                self.on_edge = False
            
            def dilate(self):
                bb.dilate(self.bb, self.dir)
            
            def should_commit(self):
                return self.capped

            def should_keep_dilating(self):
                self.on_edge = len(set(self.dir) & set(bb.on_edge(self.bb))) > 0
                self.capped = my_pieces & (bb.not_(bb.pos_mask(*pos)) & self.bb) != 0
                return not self.on_edge and not self.capped
        start = bb.pos_mask(*pos)
        states = [State(dir_, start) for dir_ in bb.directions]
        for state in states:
            while state.should_keep_dilating():
                state.dilate()
            if state.should_commit():
                if color is Color.WHITE:
                    self._white |= state.bb
                elif color is Color.BLACK:
                    self._black |= state.bb

    def __repr__(self):
        def symbol_at(row: int, col: int) -> str:
            mask = bb.pos_mask(row, col)
            if self._white & mask != 0:
                return 'W'
            elif self._black & mask != 0:
                return 'B'
            else:
                return '-'
        res = [symbol_at(r, c) for r in range(8) for c in range(8)]
        return '\n'.join(res)

async def loop(user: Player, ai_player: Player, board: Board):
    # Game initialization
    _logger.debug(repr(board))
    turn_player = user

    while True:
        _logger.info(f'Waiting for {str(turn_player)} to make a move...')
        if turn_player is ai_player:
            ai.turn.set()
        else:
            ai.turn.clear()
        move = await turn_player.move
        board.place(turn_player.color, move)
        _logger.info(f'{str(turn_player)} played {move}')
        # Toggle turn_player
        turn_player = user if turn_player is ai_player else ai_player