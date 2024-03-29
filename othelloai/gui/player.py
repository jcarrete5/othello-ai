"""Player implementation for a user using the GUI."""

import threading
from typing import Callable, Optional

from ..bitboard import Position
from ..board import Board
from ..color import Color
from ..exception import OutOfTurnError, PlayerInterrupted
from ..player import Player


class GUIPlayer(Player):
    """Player that makes moves from the GUI."""

    def __init__(
        self,
        color: Color,
        on_board_changed_callback: Callable[[Board], None],
        on_game_over_callback: Callable[[Optional[Color], Board], None],
    ):
        super().__init__(color)
        self._on_board_changed_callback = on_board_changed_callback
        self._on_game_over_callback = on_game_over_callback
        self._move: Optional[Position] = None
        self._move_made_event = threading.Event()
        self._can_move_event = threading.Event()

    def _get_move(self, board: Board, interrupt: threading.Event):
        while not self._move_made_event.wait(0.1):
            if interrupt.is_set():
                raise PlayerInterrupted
        assert self._move is not None
        pos = self._move
        self._move_made_event.clear()
        return pos

    def make_move(self, pos: Position):
        """Signal that a move has been made."""
        if not self._can_move_event.is_set():
            raise OutOfTurnError
        assert (
            not self._move_made_event.is_set()
        ), "Cannot set a move if a move has already been made"
        self._move = pos
        self._move_made_event.set()
        self._can_move_event.clear()

    def _on_board_changed(self, board: Board):
        self._on_board_changed_callback(board)

    def _on_game_over(self, color: Optional[Color], board: Board):
        self._on_game_over_callback(color, board)

    def _on_turn_change(self, turn_player_color: Color):
        if self.color == turn_player_color:
            self._can_move_event.set()

    def _on_illegal_move(self):
        # If the player made an illegal move, let them try again
        self._can_move_event.set()
