from __future__ import annotations

import pytest

from othelloai import bitboard as bb
from othelloai.game import Board, BoardState, IllegalMoveError
from othelloai.player import Color


def test_place_and_capture():
    board = Board(BoardState())
    pos = bb.Position(0, 0)
    with pytest.raises(IllegalMoveError):
        board.place(Color.WHITE, pos)
    # TODO more tests
