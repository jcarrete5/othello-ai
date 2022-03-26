import pytest

from threading import Timer, Event

from othelloai.board import Board, Color
from othelloai.ai.minmax_cpp import MinmaxAIPlayerCPP

class TimedTest:
    def __init__(self, timeout):
        self.timeout = timeout

    def __enter__(self):
        self.timer = Timer(self.timeout, lambda: pytest.fail("AI timed out.."))
        self.timer.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.timer.cancel()

def test_place_and_capture():
    board = Board()
    black_player = MinmaxAIPlayerCPP(Color.black, 3)
    white_player = MinmaxAIPlayerCPP(Color.white, 3)

    turn_player = black_player
    board.turn_player_color = turn_player.color

    move = None
    for _ in range(3):
        # get move
        with TimedTest(10.0):
            move = turn_player.get_move(board.copy(), Event())
        # play move and switch players
        if move:
            board.place(board.turn_player_color, move)
            turn_player = white_player if turn_player.color == Color.black else black_player
            board.turn_player_color = turn_player.color
        else:
            pytest.fail("No move")

