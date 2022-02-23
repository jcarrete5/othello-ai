"""Implementations for objects that provide moves."""

import enum
import threading
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

from .ai import Strategy

if TYPE_CHECKING:
    from .bitboard import Position
    from .game import BoardState


class Color(enum.Enum):
    BLACK = enum.auto()
    WHITE = enum.auto()


class Mover(ABC):
    """ABC to get and make moves for a player."""

    @abstractmethod
    def get_move(self) -> Optional["Position"]:
        raise NotImplementedError

    @abstractmethod
    def set_move(self, value: "Position"):
        raise NotImplementedError


class SynchronizedMover(Mover):
    """
    Getting and making moves are synchronized.

    A move can only be gotten after it has been set and a move can only
    be set if it is not already set.
    """

    def __init__(self, interrupt_event: threading.Event = None):
        self._move_event = threading.Event()
        self._interrupt_event = interrupt_event
        self._move: Optional["Position"] = None

    def get_move(self):
        while not self._move_event.wait(1):
            if self._interrupt_event is None or self._interrupt_event.is_set():
                return None
        move = self._move
        self._move_event.clear()
        return move

    def set_move(self, value):
        assert (
            not self._move_event.is_set()
        ), "Cannot set a move if a move has already been set"
        self._move = value
        self._move_event.set()


class ComputerMover(Mover):
    """
    Moves are gotten from a strategy function.

    Cannot set moves.
    """

    def __init__(self, strategy: Strategy, state: "BoardState"):
        self._strategy = strategy
        self._board_state = state

    def get_move(self):
        return self._strategy(self._board_state)

    def set_move(self, value):
        assert False, "Can't set a move"


class Player:
    def __init__(self, color: Color, mover: Mover):
        self._color = color
        self._mover = mover

    @property
    def color(self):
        return self._color

    def get_move(self):
        return self._mover.get_move()

    def make_move(self, value: "Position"):
        self._mover.set_move(value)


def make_local_player(color: Color, interrupt_event: threading.Event = None):
    return Player(color, SynchronizedMover(interrupt_event))


def make_computer_player(color: Color, strategy: Strategy, board_state: "BoardState"):
    return Player(color, ComputerMover(strategy, board_state))
