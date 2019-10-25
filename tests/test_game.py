from __future__ import annotations
# from typing import TYPE_CHECKING
import pytest
from othelloai.game import Board, BoardState, IllegalMoveError
from othelloai.player import Color
from othelloai import bitboard as bb


def test_place_and_capture():
    board = Board(BoardState())
    pos = bb.Position(0, 0)
    with pytest.raises(IllegalMoveError):
        board.place(Color.WHITE, pos)
    # TODO more tests
