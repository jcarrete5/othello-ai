"""Core game logic."""

import cProfile
import enum
import logging
import threading

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
                self._notify(EventType.board_change, self._board.copy())
                _logger.info("%s played %s", turn_player, move)
            except PassMove:
                _logger.info("%s passed their move", turn_player)
            except IllegalMoveError:
                _logger.info("%s attempted an illegal move", turn_player)
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

    def _notify(self, e: EventType, *args):
        if e is EventType.board_change:
            (board,) = args
            assert isinstance(board, Board), f"Incorrect arguments for {e}: {args}"
            self._my_player.signal_board_change(board)
            self._opponent_player.signal_board_change(board)
        elif e is EventType.game_over:
            color, board = args
            assert (
                isinstance(color, Color) or color is None
            ), f"Incorrect arguments for {e}: {args}"
            assert isinstance(board, Board), f"Incorrect arguments for {e}: {args}"
            self._my_player.signal_game_over(color, board)
            self._opponent_player.signal_game_over(color, board)
        else:
            assert False, f"{e} not implemented"

    def _is_game_over(self) -> bool:
        filled = self._board.empty_cells() == 0  # No empty cells i.e. all spaces filled
        no_white = self._board.white == 0
        no_black = self._board.black == 0

        if filled:
            white_count = self._board.white.bit_count()
            black_count = self._board.black.bit_count()
            if white_count > black_count:
                self._notify(EventType.game_over, Color.white, self._board.copy())
            elif white_count < black_count:
                self._notify(EventType.game_over, Color.black, self._board.copy())
            else:
                self._notify(EventType.game_over, None, self._board.copy())
        elif no_white:
            self._notify(EventType.game_over, Color.black, self._board.copy())
        elif no_black:
            self._notify(EventType.game_over, Color.white, self._board.copy())

        return filled or no_white or no_black

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
