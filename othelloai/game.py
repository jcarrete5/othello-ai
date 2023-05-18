"""Core game logic."""

import cProfile
import enum
import logging
import threading
from typing import Optional

from .args import get_args
from .board import Board
from .color import Color
from .exception import IllegalMoveError, PassMove, PlayerInterrupted
from .player import Player

_logger = logging.getLogger(__name__)


class EventType(enum.Enum):
    """Events emitted by the game that players can observe."""

    board_change = enum.auto()
    game_over = enum.auto()
    turn_change = enum.auto()


class GameType(enum.Enum):
    """Type of the game to play."""

    computer = enum.auto()
    online = enum.auto()


class Game:
    """Core game logic loop."""

    # Used to differentiate different game threads in logs
    game_counter = 0

    def __init__(
        self,
        my_player: Player,
        opponent_player: Player,
        board: Board = None,
    ):
        Game.game_counter += 1
        self._my_player = my_player
        self._opponent_player = opponent_player
        self._board = board if board is not None else Board()
        self._both_players_passed = False
        self._runner = threading.Thread(
            target=self._profile_loop if get_args().is_profiling_enabled else self.loop,
            name=f"GameThread ({Game.game_counter})",
        )
        self._game_stopped_event = threading.Event()

    def _profile_loop(self):
        with cProfile.Profile() as profile:
            self.loop()
        profile.dump_stats(get_args().profile_dir / "game-thread.profile")

    def loop(self):
        """
        Run main game loop.

        Players alternate making moves on the board.
        """
        # Send initial board state
        self._notify(EventType.board_change, self._board.copy())
        self._notify(EventType.turn_change, self._board.turn_player_color)

        passed_previous = False
        turn_player = (
            self._my_player
            if self._my_player.color is self._board.turn_player_color
            else self._opponent_player
        )
        while not self._game_stopped_event.is_set() and not self._is_game_over():
            _logger.info("Waiting for %s to make a move", turn_player)

            try:
                move = turn_player.get_move(
                    self._board.copy(), self._game_stopped_event
                )
                self._board.place(turn_player.color, move)
                passed_previous = False
                _logger.info("%s played %s", turn_player, move)
            except PassMove:
                if passed_previous:
                    self._both_players_passed = True
                else:
                    passed_previous = True
                _logger.info("%s passed their move", turn_player)
            except IllegalMoveError:
                _logger.info("%s attempted an illegal move", turn_player)
                turn_player.signal_illegal_move_made()
                continue
            except PlayerInterrupted:
                _logger.debug("%s interrupted during their move", turn_player)
                continue

            # Swap turn players
            turn_player = (
                self._my_player
                if turn_player is self._opponent_player
                else self._opponent_player
            )
            self._board.swap_turn_players()
            self._notify(EventType.turn_change, self._board.turn_player_color)
            self._notify(EventType.board_change, self._board.copy())

        white_count = self._board.white.bit_count()
        black_count = self._board.black.bit_count()
        _logger.info("Game Over. white: %d, black: %d", white_count, black_count)
        self._notify(EventType.game_over, self.winner(), self._board.copy())

    def _notify(self, e: EventType, *args):
        err_str = f"Incorrect arguments for {e}: {args}"
        if e is EventType.board_change:
            (board,) = args
            assert isinstance(board, Board), err_str
            self._my_player.signal_board_change(board)
            self._opponent_player.signal_board_change(board)
        elif e is EventType.game_over:
            color, board = args
            assert isinstance(color, Color) or color is None, err_str
            assert isinstance(board, Board), err_str
            self._my_player.signal_game_over(color, board)
            self._opponent_player.signal_game_over(color, board)
        elif e is EventType.turn_change:
            (color,) = args
            assert isinstance(color, Color), err_str
            self._my_player.signal_turn_change(color)
            self._opponent_player.signal_turn_change(color)
        else:
            assert False, f"{e} not implemented"

    def _is_game_over(self) -> bool:
        return self._board.empty_cells() == 0 or self._both_players_passed

    def winner(self) -> Optional[Color]:
        if not self._is_game_over():
            return None
        white_count = self._board.white.bit_count()
        black_count = self._board.black.bit_count()
        if white_count > black_count:
            winner = Color.white
        elif white_count < black_count:
            winner = Color.black
        else:
            winner = None
        return winner

    def shutdown(self):
        """Cleanup resources required by the game and wait for completion."""
        assert not self._game_stopped_event.is_set(), "Game already shutdown"
        self._game_stopped_event.set()
        _logger.debug("Game stopped event set")
        self._runner.join()
        _logger.debug("Game stopped")

    def start(self):
        """Start game loop."""
        assert not self._runner.is_alive(), "Game already started"
        self._runner.start()
        _logger.debug("New game started")
