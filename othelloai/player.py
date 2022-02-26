"""Player abstract base class definition."""

import threading
from abc import ABC, abstractmethod

from .exception import IllegalMoveError, PassMove
from .bitboard import Position
from .board import Board
from .color import Color


class Player(ABC):
    """Serves as an interface to communicate with a game."""

    def __init__(self, color: Color):
        """Construct a player with a color."""
        self._color = color

    @property
    def color(self) -> Color:
        """Player's color."""
        return self._color

    def get_move(self, board: Board, interrupt: threading.Event) -> Position:
        """
        Request a move from this player.

        The returned position is checked for validity against the board
        and this player's turn is automatically passed if there are no
        valid moves.
        """
        valid_moves = board.valid_moves()
        if not valid_moves:
            raise PassMove
        pos = self._get_move(board, interrupt)
        if pos not in valid_moves:
            raise IllegalMoveError
        return pos

    @abstractmethod
    def _get_move(self, board: Board, interrupt: threading.Event) -> Position:
        """Return a move from this player."""
        ...

    def signal_board_change(self, board: Board):
        """Signal when the board has been changed."""
        self._on_board_changed(board)

    def _on_board_changed(self, board: Board):
        """Override to observe board change events."""
        ...

    def __str__(self):
        return self.color.name
