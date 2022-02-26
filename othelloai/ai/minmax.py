"""Minmax AI implementation."""

import threading
from math import inf
from typing import Optional

from ..bitboard import Position
from ..board import Board
from ..color import Color, opposite_color
from ..player import Player


class MinmaxAIPlayer(Player):
    """Player that uses the minmax algorithm to make moves."""

    def __init__(self, color: Color, depth: int):
        super().__init__(color)
        self._depth = depth

    def _get_move(self, board: Board, interrupt: threading.Event) -> Position:
        _, best_move = self._find_best_move(board, self._depth)
        return best_move

    def _evaluate_state(self, state: Board) -> int:
        my_pieces = state.white if self.color == Color.white else state.black
        opponent_pieces = state.black if self.color == Color.white else state.white
        return my_pieces.bit_count() - opponent_pieces.bit_count()

    def _find_best_move(self, board: Board, depth: int) -> (int, Optional[Position]):
        current_score = self._evaluate_state(board)
        potential_moves = board.valid_moves()
        if not potential_moves or depth == 0:
            return current_score, None

        best_move = potential_moves[0]
        best_score = -inf
        color = board.turn_player_color
        for move in potential_moves:
            initial_state = board.copy()

            board.place(color, move)
            board.turn_player_color = opposite_color(color)

            opponent_best_score, _ = self._find_best_move(board, depth - 1)
            current_score = -opponent_best_score

            if current_score > best_score:
                best_score = current_score
                best_move = move

            board = initial_state

        return best_score, best_move
