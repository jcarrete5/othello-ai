"""Strategies and implementation details for the AI."""

from random import choice as choose_from
from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from . import bitboard as bb
    from .game import BoardState


# An AI strategy function:
#   - must adhere to the Strategy type
#   - MUST NOT modify the board state
Strategy = Callable[["BoardState"], Optional["bb.Position"]]


def random(state: "BoardState") -> Optional["bb.Position"]:
    """Return a random valid move or None if no moves are possible."""
    try:
        return choose_from(state.valid_moves())
    except IndexError:
        return None
