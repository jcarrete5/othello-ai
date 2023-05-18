import pytest

from threading import Event
import logging

from othelloai.main import setup_logging
from othelloai.game import Game, Board, Color
from othelloai.ai.minmax_cpp import MinmaxAIPlayerCPP
from othelloai.ai.random import RandomAIPlayer

setup_logging()
_logger = logging.getLogger(__name__)

def test_move_generation_and_place():
    board = Board()
    black_player = MinmaxAIPlayerCPP(Color.black, 5)
    board.turn_player_color = Color.black
    move = black_player.get_move(board.copy(), Event())
    board.place(board.turn_player_color, move)

def test_game():
    white_wins = 0
    black_wins = 0
    ties = 0
    for _ in range(100):
        game = Game(MinmaxAIPlayerCPP(Color.white, 5), RandomAIPlayer(Color.black), Board())
        game.loop()
        if game.winner() == Color.white:
            white_wins = white_wins + 1
        elif game.winner() == Color.black:
            black_wins = black_wins + 1
        else:
            ties = ties + 1
    _logger.info(f"white wins: {white_wins}, black wins: {black_wins}, ties: {ties}")

