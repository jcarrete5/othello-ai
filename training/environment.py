from typing import Any

from othelloai.board import Board

from tf_agents.environments import PyEnvironment
from tf_agents.trajectories import time_step as ts
from tf_agents.typing import types


class OthelloEnvironment(PyEnvironment):
    def __init__(self):
        super().__init__()
        self._board = Board()

    def observation_spec(self) -> types.NestedArraySpec:
        pass

    def action_spec(self) -> types.NestedArraySpec:
        pass

    def get_info(self) -> types.NestedArray:
        pass

    def get_state(self) -> Any:
        pass

    def set_state(self, state: Any) -> None:
        pass

    def _step(self, action: types.NestedArray) -> ts.TimeStep:
        pass

    def _reset(self) -> ts.TimeStep:
        pass
