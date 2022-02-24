from __future__ import annotations

import pytest

from othelloai import bitboard as bb
from othelloai.board import Board
from othelloai.player import Color
from othelloai.exception import IllegalMoveError


def test_place_and_capture():
    board = Board()
    pos = bb.Position(0, 0)
    with pytest.raises(IllegalMoveError):
        board.place(Color.white, pos)
    # TODO more tests
