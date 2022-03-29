import pytest

from othelloai import bitboard as bb
from othelloai.board import Board
from othelloai.player import Color
from othelloai.exception import IllegalMoveError


def test_place_illegal_move():
    board = Board()
    pos = bb.Position(0, 0)
    with pytest.raises(IllegalMoveError):
        board.place(Color.white, pos)
'''
    pos = bb.Position(3, 3)
    with pytest.raises(IllegalMoveError):
        board.place(Color.white, pos)
'''


def test_place_and_capture():
    board = Board(init_white=0x0000101810200000, init_black=0x0000000028000000)
    pos = bb.Position(2, 4)
    board.place(Color.black, pos)
    assert board.white == 0x0000100010200000 and board.black == 0x0000081828000000
