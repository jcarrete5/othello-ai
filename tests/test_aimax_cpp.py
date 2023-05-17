import pytest

from threading import Event

from othelloai.main import setup_logging
from othelloai.game import Game, Board, Color
from othelloai.ai.minmax_cpp import MinmaxAIPlayerCPP
from othelloai.ai.random import RandomAIPlayer

def test_move_generation_and_place():
    board = Board()
    black_player = MinmaxAIPlayerCPP(Color.black, 5)
    board.turn_player_color = Color.black
    move = black_player.get_move(board.copy(), Event())
    board.place(board.turn_player_color, move)

def test_game():
    setup_logging()
    game = Game(MinmaxAIPlayerCPP(Color.white, 5), RandomAIPlayer(Color.black), Board())
    game.loop()

