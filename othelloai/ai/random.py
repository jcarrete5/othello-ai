"""Random AI implementation."""

import threading
from random import choice as choose_from

from ..board import Board
from ..player import Player
from ..exception import PassMove


class RandomAIPlayer(Player):
    """Player that makes random valid moves."""

    def _get_move(self, board: Board, interrupt: threading.Event):
        try:
            return choose_from(board.valid_moves())
        except IndexError:
            raise PassMove
