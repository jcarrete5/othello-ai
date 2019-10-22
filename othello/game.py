from __future__ import annotations
import logging
import re
import threading
import asyncio
import enum
from typing import List, Callable
from othello import bitboard as bb
from othello.player import Color, Player

_LOGGER = logging.getLogger(__name__)


class GameType(enum.Enum):
    COMPUTER = enum.auto()
    ONLINE = enum.auto()


class IllegalMoveError(Exception):
    """ Raised when an illegal move is attempted. """


class BoardState:
    """ Thread-safe way to access board state. """
    def __init__(self, init_white=0, init_black=0, turn_player_color=Color.BLACK):
        self._white_lock = threading.Lock()
        self._white = init_white
        self._black_lock = threading.Lock()
        self._black = init_black
        self._change_callbacks = set()
        self._turn_player_color_lock = threading.Lock()
        self._turn_player_color = turn_player_color

    def empty_cells(self) -> int:
        return bb.not_(self.white | self.black)

    def valid_moves(self) -> List[bb.Position]:
        """ Return a list of positions of valid moves for the turn player. """
        if self._turn_player_color is Color.BLACK:
            my_pieces = self.black
            foe_pieces = self.white
        else:
            my_pieces = self.white
            foe_pieces = self.black
        moves_bb = 0x0
        for dir_ in bb.DIRECTIONS:
            candidates = foe_pieces & bb.shift(my_pieces, dir_)
            while candidates != 0:
                shifted = bb.shift(candidates, dir_)
                moves_bb |= self.empty_cells() & shifted
                candidates = foe_pieces & shifted
        return bb.to_list(moves_bb)

    def _changed(self):
        """ Called when the state of the board changes. """
        for callback in self._change_callbacks:
            callback(self._white, self._black, self._turn_player_color)

    def onchange(self, func: Callable[int, int, Color]):
        """ Adds func to a list of callbacks to be called on state change. """
        self._change_callbacks.add(func)
        return func

    def remove_onchange(self, func: Callable[int, int, Color]):
        self._change_callbacks.remove(func)

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

    @property
    def turn_player_color(self):
        with self._turn_player_color_lock:
            return self._turn_player_color

    @turn_player_color.setter
    def turn_player_color(self, value: Color):
        with self._turn_player_color_lock:
            self._turn_player_color = value
            self._changed()

    def __eq__(self, other: BoardState):
        return \
            self.white == other.white \
            and self.black == other.black \
            and self.turn_player_color == other.turn_player_color

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

    def place(self, color: Color, pos: bb.Position):
        """ Place a piece of color `color` at position `pos`

        Raises an IllegalMoveError if an illegal move was attempted
        """
        assert 0 <= pos.row < 8
        assert 0 <= pos.col < 8
        pos_mask = bb.pos_mask(*pos)
        self._capture(color, pos)
        if color is Color.BLACK:
            self.board_state.black |= pos_mask
        else:
            self.board_state.white |= pos_mask

    def _capture(self, color: Color, pos: bb.Position):
        """
        Find pieces that should be captured by playing `color`
        at `pos` and capture those pieces

        Raises an IllegalMoveError if an illegal move was attempted
        """
        my_pieces = self.board_state.white if color is Color.WHITE else self.board_state.black
        empty = self.board_state.empty_cells()
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
        did_commit = False
        for state in states:
            while state.should_keep_dilating():
                state.dilate()
            if state.should_commit():
                did_commit = True
                if color is Color.WHITE:
                    self.board_state.white |= state.bb
                    self.board_state.black &= bb.not_(state.bb)
                elif color is Color.BLACK:
                    self.board_state.black |= state.bb
                    self.board_state.white &= bb.not_(state.bb)
        if not did_commit:
            raise IllegalMoveError

    def __str__(self):
        return str(self.board_state)


class Game(threading.Thread):
    game_counter = 0

    def __init__(self, board_state: BoardState, my_color: Color, type_: GameType):
        super().__init__(name=f'GameThread ({Game.game_counter})')
        Game.game_counter += 1
        self.board_state = board_state
        self.my_player = Player(my_color)
        self._board = Board(self.board_state)
        self._interrupted = threading.Event()
        self._type = type_

    def interrupt(self):
        self._interrupted.set()

    async def loop(self):
        # Set opponent color to be opposite mine
        opponent = Player(list(set(Color).remove(self.my_player.color))[0])
        turn_player = self.my_player if self.my_player.color is Color.BLACK else opponent
        while not self._interrupted.is_set():
            move = await turn_player.move
            self._board.place(turn_player.color, move)
            # Change to other player
            turn_player = self.my_player if turn_player is opponent else opponent
            # Change board state to reflect new player

    def run(self):
        _LOGGER.info('New game started')
        asyncio.run(self.loop(), debug=True)
        _LOGGER.info('Game ended')
