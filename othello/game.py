from __future__ import annotations
import logging
import re
import threading
import asyncio
import enum
from typing import List, Callable
from othello import bitboard as bb
from othello.player import Color, Player, AIPlayer

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)


class GameType(enum.Enum):
    COMPUTER = enum.auto()
    ONLINE = enum.auto()


class IllegalMoveError(Exception):
    """ Raised when an illegal move is attempted. """


class BoardState:
    """ Thread-safe way to access board state. """
    def __init__(self, init_white=0, init_black=0, turn_player_color=Color.BLACK):
        self._white_lock = threading.RLock()
        self._white = init_white
        self._black_lock = threading.RLock()
        self._black = init_black
        self._change_callbacks = set()
        self._turn_player_color_lock = threading.RLock()
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
            callback(self.white, self.black)

    def onchange(self, func: Callable[int, int]):
        """ Adds func to a list of callbacks to be called on state change.

        Not called when the turn_player_color changes.
        """
        self._change_callbacks.add(func)
        return func

    def remove_onchange(self, func: Callable[int, int]):
        self._change_callbacks.remove(func)

    def reset(self):
        self.white = 0
        self.black = 0
        self.turn_player_color = Color.BLACK

    @property
    def white(self) -> int:
        _LOGGER.debug('Waiting for white lock')
        with self._white_lock:
            _LOGGER.debug('Acquire white lock')
            return self._white

    @white.setter
    def white(self, value: int):
        _LOGGER.debug('Waiting for white lock')
        with self._white_lock:
            _LOGGER.debug('Acquire white lock')
            self._white = value
        self._changed()

    @property
    def black(self) -> int:
        _LOGGER.debug('Waiting for black lock')
        with self._black_lock:
            _LOGGER.debug('Acquire black lock')
            return self._black

    @black.setter
    def black(self, value: int):
        _LOGGER.debug('Waiting for black lock')
        with self._black_lock:
            _LOGGER.debug('Acquire black lock')
            self._black = value
        self._changed()

    @property
    def turn_player_color(self):
        _LOGGER.debug('Waiting for turn player color lock')
        with self._turn_player_color_lock:
            _LOGGER.debug('Acquire turn player color lock')
            return self._turn_player_color

    @turn_player_color.setter
    def turn_player_color(self, value: Color):
        _LOGGER.debug('Waiting for turn player color lock')
        with self._turn_player_color_lock:
            _LOGGER.debug('Acquire turn player color lock')
            self._turn_player_color = value

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
        self.my_player = None
        self._loop = None
        self._my_color = my_color
        self._board = Board(self.board_state)
        self._type = type_

    def interrupt(self):
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        else:
            _LOGGER.warning('Game event loop was interrupted before it was running')

    async def loop(self):
        self._loop = asyncio.get_running_loop()
        # def handler(loop, ctx):
        #     _LOGGER.error(ctx.message)
        #     loop.stop()
        # self._loop.set_exception_handler(handler)

        self.my_player = Player(self._my_color)
        # Set opponent color to be opposite mine
        opp_color = list(Color)[0] if list(Color)[0] is not self.my_player.color else list(Color)[1]
        if self._type is GameType.COMPUTER:
            opponent = AIPlayer(opp_color, self.board_state)
        else:
            raise RuntimeError(f'{self._type} is not implemented')

        turn_player = self.my_player if self.my_player.color is Color.BLACK else opponent
        while self._loop.is_running():
            _LOGGER.info('Waiting for %s to make a move', turn_player)
            move = await turn_player.move
            if move is not None:
                _LOGGER.info('%s played %s', turn_player, move)
                self._board.place(turn_player.color, move)
            else:
                _LOGGER.info('%s passed their move', str(turn_player))

            # Artificial delay so moves don't appear instantly
            await asyncio.sleep(0.4)

            # Change to other player
            turn_player = self.my_player if turn_player is opponent else opponent
            self.board_state.turn_player_color = turn_player.color

    def run(self):
        _LOGGER.info('New game started')
        try:
            asyncio.run(self.loop())
        except RuntimeError as err:
            _LOGGER.warning(err)
            self.board_state.reset()
        finally:
            _LOGGER.info('Game ended')
