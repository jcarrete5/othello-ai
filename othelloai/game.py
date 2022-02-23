"""Core game logic."""

from __future__ import annotations

import enum
import logging
import re
import threading
from typing import TYPE_CHECKING

from . import ai
from . import bitboard as bb
from .player import Color, make_computer_player, Player

if TYPE_CHECKING:
    from queue import Queue

_logger = logging.getLogger(__name__)


class EventType(enum.Enum):
    board_changed = enum.auto()


class GameType(enum.Enum):
    computer = enum.auto()
    online = enum.auto()


class IllegalMoveError(Exception):
    """Raised when an illegal move is attempted."""


class BoardState:
    def __init__(self, init_white=0, init_black=0, turn_player_color=Color.BLACK):
        self.white = init_white
        self.black = init_black
        self.turn_player_color = turn_player_color

    def empty_cells(self) -> int:
        """Return a bitboard representing empty cells."""
        return bb.not_(self.white | self.black)

    def valid_moves(self) -> list[bb.Position]:
        """Return a list of positions of valid moves for the turn player."""
        if self.turn_player_color is Color.BLACK:
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

    def reset(self):
        self.white = 0
        self.black = 0
        self.turn_player_color = Color.BLACK

    def __eq__(self, other: BoardState):
        return (
            self.white == other.white
            and self.black == other.black
            and self.turn_player_color == other.turn_player_color
        )

    def __str__(self):
        def symbol_at(row: int, col: int) -> str:
            mask = bb.pos_mask(row, col)
            if self.white & mask != 0:
                return "\u2588"
            elif self.black & mask != 0:
                return "\u2591"
            else:
                return "-"

        res = [symbol_at(r, c) for r in range(8) for c in range(8)]
        return "\n".join(re.findall("........", "".join(res)))


class Board:
    """Logic for placing moves and manipulating board state."""

    def __init__(self, board_state: BoardState):
        self.board_state = board_state

    def place(self, color: Color, pos: bb.Position):
        """Place a piece of color `color` at position `pos`.

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
        """Find pieces that should be captured.

        It does this by playing `color` at `pos` and capture those pieces.
        Raises an IllegalMoveError if an illegal move was attempted.
        """
        my_pieces = (
            self.board_state.white if color is Color.WHITE else self.board_state.black
        )
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


class Game:
    """Core game logic loop."""

    # Used to differentiate different game threads in logs
    game_counter = 0

    def __init__(
        self,
        board_state: BoardState,
        my_player: Player,
        type_: GameType,
        out_queue: Queue = None,
        ai_strategy: ai.Strategy = None,
    ):
        Game.game_counter += 1
        self.board_state = board_state
        self._my_player = my_player
        self._board = Board(self.board_state)
        self._type = type_
        self._out_queue = out_queue
        self._runner = threading.Thread(
            target=self.loop, name=f"GameThread ({Game.game_counter})"
        )
        self._game_stopped_event = threading.Event()

        # Set opponent color to be opposite my_player
        opp_color = (
            list(Color)[0]
            if list(Color)[0] is not self._my_player.color
            else list(Color)[1]
        )
        if self._type is GameType.computer:
            assert (
                ai_strategy
            ), "AI strategy must not be None when playing against a computer"
            self.opponent = make_computer_player(
                opp_color, ai_strategy, self.board_state
            )
        else:
            assert False, f"{self._type} is not implemented"

    def loop(self):
        # Send initial board state
        if self._out_queue:
            self._out_queue.put(
                (
                    EventType.board_changed,
                    self.board_state.white,
                    self.board_state.black,
                )
            )

        turn_player = (
            self._my_player if self._my_player.color is Color.BLACK else self.opponent
        )
        while not self._game_stopped_event.is_set():
            _logger.info("Waiting for %s to make a move", turn_player)

            move = turn_player.get_move()  # May block

            if move is not None:
                _logger.info("%s played %s", turn_player, move)
                self._board.place(turn_player.color, move)
            else:
                _logger.info("%s passed their move", str(turn_player))

            if self._out_queue:
                self._out_queue.put(
                    (
                        EventType.board_changed,
                        self.board_state.white,
                        self.board_state.black,
                    )
                )

            # Change to other player
            turn_player = (
                self._my_player if turn_player is self.opponent else self.opponent
            )
            self.board_state.turn_player_color = turn_player.color

    def shutdown(self):
        assert not self._game_stopped_event.is_set(), "Game already shutdown"
        self._game_stopped_event.set()
        _logger.debug("Game stopped event set")
        self._runner.join()
        _logger.info("Game stopped")

    def start(self):
        assert not self._runner.is_alive(), "Game already started"
        self._runner.start()
        _logger.info("New game started")
