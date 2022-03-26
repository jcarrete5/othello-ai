"""Minmax AI implementation."""

import threading
from math import inf
from typing import Optional

from ..bitboard import Position, pos_mask
from ..board import Board
from ..color import Color
from ..player import Player

import othello_cpp

def color_at(board: Board, pos: Position):
    mask = pos_mask(pos.row, pos.col)
    if board.white & mask:
        return Color.white
    if board.black & mask:
        return Color.black
    return None

def py_color_to_cpp_color(color: Optional[Color]):
    if color == Color.white:
        return othello_cpp.Color.WHITE
    elif color == Color.black:
        return othello_cpp.Color.BLACK
    else:
        return othello_cpp.Color.NONE

def py_board_to_cpp_board(board: Board):
    cpp_board = othello_cpp.GameBoard()
    for row in range(0,8):
        for col in range(0,8):
            py_pos = Position(row, col)
            py_col = color_at(board, py_pos)
            cpp_pos = othello_cpp.Position(row, col)
            cpp_col = py_color_to_cpp_color(py_col)
            cpp_board.set(cpp_pos, cpp_col)
    return cpp_board

def cpp_position_to_py_position(position: othello_cpp.Position):
    return Position(position.row, position.col)

class MinmaxAIPlayerCPP(Player):
    """Player that uses the minmax algorithm to make moves."""

    def __init__(self, color: Color, depth: int, **kwargs):
        super().__init__(color, **kwargs)
        self._depth = depth

    def _get_move(self, board: Board, interrupt: threading.Event) -> Position:
        cpp_board = py_board_to_cpp_board(board)
        cpp_color = py_color_to_cpp_color(self._color)
        best_move_pos = othello_cpp.AIMax_best_move(cpp_color, cpp_board, self._depth)
        return cpp_position_to_py_position(best_move_pos)

