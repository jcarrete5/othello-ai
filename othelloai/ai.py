from __future__ import annotations
from random import choice as chooseFrom
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from othello import bitboard as bb
    from othello.game import BoardState

def random(state: BoardState) -> bb.Position:
    """ Returns a random valid move or None if no moves are possible. """
    try:
        return chooseFrom(state.valid_moves())
    except IndexError:
        return None
