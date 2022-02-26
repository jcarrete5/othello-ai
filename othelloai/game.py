"""Core game logic."""

import enum
import logging
import threading
from copy import copy

from .board import Board
from .exception import IllegalMoveError, PassMove, PlayerInterrupted
from .player import Player

_logger = logging.getLogger(__name__)


class EventType(enum.Enum):
    """Events emitted by the game that players can observe."""

    board_change = enum.auto()


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
            target=self.loop, name=f"GameThread ({Game.game_counter})"
        )
        self._game_stopped_event = threading.Event()

    def loop(self):
        """
        Run main game loop.

        Players alternate making moves on the board.
        """
        # Send initial board state
        self._notify(EventType.board_change)

        turn_player = (
            self._my_player
            if self._my_player.color is self._board.turn_player_color
            else self._opponent_player
        )
        while not self._game_stopped_event.is_set():
            _logger.info("Waiting for %s to make a move", turn_player)

            try:
                move = turn_player.get_move(self._board.copy(), self._game_stopped_event)
                self._board.place(turn_player.color, move)
                self._notify(EventType.board_change)
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

    def _notify(self, e: EventType):
        if e == EventType.board_change:
            self._my_player.signal_board_change(copy(self._board))
            self._opponent_player.signal_board_change(copy(self._board))
        else:
            assert False, f"{e} not implemented"

    def shutdown(self):
        """Cleanup resources required by the game and wait for completion."""
        assert not self._game_stopped_event.is_set(), "Game already shutdown"
        self._game_stopped_event.set()
        _logger.debug("Game stopped event set")
        self._runner.join()
        _logger.info("Game stopped")

    def start(self):
        """Start game loop."""
        assert not self._runner.is_alive(), "Game already started"
        self._runner.start()
        _logger.info("New game started")
