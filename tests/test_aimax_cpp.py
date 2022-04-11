import pytest

from threading import Event

from othelloai.board import Board, Color
from othelloai.ai.minmax_cpp import MinmaxAIPlayerCPP

def test_place_and_capture():
    board = Board()
    black_player = MinmaxAIPlayerCPP(Color.black, 15)
    board.turn_player_color = Color.black
    move = black_player.get_move(board.copy(), Event())
    board.place(board.turn_player_color, move)

