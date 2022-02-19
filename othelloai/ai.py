"""Strategies and implementation details for the AI."""

from random import choice as choose_from
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from . import bitboard as bb
    from .game import BoardState


async def random(state: BoardState) -> Optional[bb.Position]:
    """Return a random valid move or None if no moves are possible."""
    try:
        return choose_from(state.valid_moves())
    except IndexError:
        return None
