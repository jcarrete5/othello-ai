from __future__ import annotations
import logging
import re
import threading
from typing import TYPE_CHECKING, List
from othello import bitboard as bb

if TYPE_CHECKING:
    from othello.player import Color, Player

_LOGGER = logging.getLogger(__name__)


class IllegalMoveError(Exception):
    """ Raised when an illegal move is attempted. """


class BoardState:
    """ Thread-safe way to access board state. """
    def __init__(self, init_white=0, init_black=0):
        self._white_lock = threading.Lock()
        self._white = init_white
        self._black_lock = threading.Lock()
        self._black = init_black
        self._change_callbacks = set()

    def _changed(self):
        """ Called when the state of the board changes. """
        for callback in self._change_callbacks:
            callback(self._white, self._black)

    def onchange(self, func):
        """ Adds func to a list of callbacks to be called on state change. """
        self._change_callbacks.add(func)
        return func

    @property
    def white(self) -> int:
        with self._white_lock:
            return self._white

    @white.setter
    def white(self, value: int):
        with self._white_lock:
            self._white = value
            self._changed()

    @property
    def black(self) -> int:
        with self._black_lock:
            return self._black

    @black.setter
    def black(self, value: int):
        with self._black_lock:
            self._black = value
            self._changed()

    def __str__(self):
        def symbol_at(row: int, col: int) -> str:
            mask = bb.pos_mask(row, col)
            if self.white & mask != 0:
                return '\u2588'
            elif self.black & mask != 0:
                return '\u2591'
            else:
                return '-'
        res = [symbol_at(r, c) for r in range(8) for c in range(8)]
        return '\n'.join(re.findall('........', ''.join(res)))


class Board:
    def __init__(self, board_state: BoardState):
        self.board_state = board_state

    def empty_cells(self) -> int:
        return bb.not_(self.board_state.white | self.board_state.black)

    def valid_moves_for(self, color: Color) -> List[bb.Position]:
        if color is Color.BLACK:
            my_pieces = self.board_state.black
            foe_pieces = self.board_state.white
        else:
            my_pieces = self.board_state.white
            foe_pieces = self.board_state.black
        moves_bb = 0x0
        for dir_ in bb.DIRECTIONS:
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
            self.board_state.black |= pos_mask
        else:
            self.board_state.white |= pos_mask
        self._capture(color, pos)

    def _capture(self, color: Color, pos: bb.Position):
        """
        Find pieces that should be captured by playing `color`
        at `pos` and capture those pieces
        """
        my_pieces = self.board_state.white if color is Color.WHITE else self.board_state.black
        empty = self.empty_cells()
        class State:
            def __init__(self, dir_, init_bb=0x0):
                self.bb = init_bb
                self.dir = dir_
                self.capped = False
                self.on_edge = False
                self.on_empty = False

            def dilate(self):
                self.bb = bb.dilate(self.bb, self.dir)

            def should_commit(self):
                return self.capped

            def should_keep_dilating(self):
                selected = bb.not_(bb.pos_mask(*pos)) & self.bb
                self.on_edge = len(set(self.dir) & set(bb.on_edge(self.bb))) > 0
                self.capped = my_pieces & selected != 0
                self.on_empty = empty & selected != 0
                return not self.on_edge and not self.capped and not self.on_empty
        start = bb.pos_mask(*pos)
        states = [State(dir_, start) for dir_ in bb.DIRECTIONS]
        for state in states:
            while state.should_keep_dilating():
                state.dilate()
            if state.should_commit():
                if color is Color.WHITE:
                    self.board_state.white |= state.bb
                    self.board_state.black &= bb.not_(state.bb)
                elif color is Color.BLACK:
                    self.board_state.black |= state.bb
                    self.board_state.white &= bb.not_(state.bb)

    def __str__(self):
        return str(self.board_state)


async def loop(interrupt: threading.Event, board_state: BoardState):
    # Game initialization
    _LOGGER.debug('Init game loop')
    _LOGGER.debug('Initial board\n%s', str(board_state))
    # turn_player = user

    # while not interrupt.is_set():
    #     _LOGGER.info('Waiting for %s to make a move...', str(turn_player))
    #     if turn_player is ai_player:
    #         ai_player.turn.set()
    #     else:
    #         ai_player.turn.clear()
    #     move = await turn_player.move
    #     board.place(turn_player.color, move)
    #     _LOGGER.info('%s played %s', str(turn_player), move)
    #     # Toggle turn_player
    #     turn_player = user if turn_player is ai_player else ai_player
    _LOGGER.info('Quit game loop')
