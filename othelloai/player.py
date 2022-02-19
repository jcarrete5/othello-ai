import asyncio
import enum
from typing import TYPE_CHECKING, Callable, Coroutine, Optional, Any

if TYPE_CHECKING:
    from .bitboard import Position
    from .game import BoardState


class Color(enum.Enum):
    BLACK = enum.auto()
    WHITE = enum.auto()


class Player:
    """Interface for playing and retrieving moves asynchronously."""

    def __init__(self, color: Color):
        self._color = color
        self._loop = asyncio.get_running_loop()
        self._move = self._loop.create_future()

    @property
    def color(self):
        return self._color

    @property
    async def move(self) -> Optional["Position"]:
        """The next move this player intends to make."""
        move = await self._move
        del self.move
        return move

    @move.setter
    def move(self, value: "Position"):
        def callback():
            if self._move.done():
                raise RuntimeError(
                    f"Attempt to set {self} move but it has already been set"
                )
            self._move.set_result(value)

        self._loop.call_soon_threadsafe(callback)

    @move.deleter
    def move(self):
        self._move = self._loop.create_future()

    def __repr__(self):
        return f"Player({self._color})"


class AIPlayer(Player):
    def __init__(
        self,
        color: Color,
        state: "BoardState",
        strategy: Callable[["BoardState"], Coroutine[Any, Any, Optional["Position"]]],
    ):
        super().__init__(color)
        self._strategy = strategy
        self._state = state

    @Player.move.getter
    async def move(self):
        return await self._strategy(self._state)
