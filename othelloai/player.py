"""Player abstract base class definition."""

import threading
from abc import ABC, abstractmethod
from typing import Optional

from .bitboard import Position
from .board import Board
from .color import Color
from .exception import IllegalMoveError, PassMove


class Player(ABC):
    """Serves as an interface to communicate with a game."""

    def __init__(self, color: Color, **kwargs):
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

    def signal_game_over(self, color: Optional[Color], board: Board):
        """
        Signal when the game is over.

        color is the color of the winner or None is the game ended in a draw.
        board is the final state of the board.
        """
        self._on_game_over(color, board)

    def _on_game_over(self, color: Optional[Color], board: Board):
        """Override to observe game over events."""
        ...

    def signal_turn_change(self, color: Color):
        """Signal when the turn player has changed."""
        self._on_turn_change(color)

    def _on_turn_change(self, color: Color):
        """Override to observe turn change events."""
        ...

    def signal_illegal_move_made(self):
        """Signal when the turn player has made an illegal move."""
        self._on_illegal_move()

    def _on_illegal_move(self):
        """Override to observe illegal move events."""
        ...

    def __str__(self):
        return self.color.name
