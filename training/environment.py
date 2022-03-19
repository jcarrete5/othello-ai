import numpy as np
from tf_agents.environments import PyEnvironment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
from tf_agents.typing import types

import othelloai.bitboard as bb
from othelloai.board import Board
from othelloai.color import Color


class OthelloEnvironment(PyEnvironment):
    def __init__(self, init_turn_player_color: Color = Color.black):
        super().__init__()
        self._init_turn_player_color = init_turn_player_color
        self._board = Board(init_turn_player_color=init_turn_player_color)
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(64,), dtype=np.float32, minimum=0, maximum=2, name="observation"
        )
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(1,), dtype=np.float32, minimum=0, maximum=1, name="action"
        )

    def _observe_board(self):
        """Return an observation from the board."""
        arr = np.zeros(shape=(64,), dtype=np.float32)
        for i in range(64):
            mask = bb.pos_mask(i // 8, i % 8)
            if self._board.black & mask > 0:
                arr[i] = Color.black.value
            elif self._board.white & mask > 0:
                arr[i] = Color.white.value
        return arr

    def observation_spec(self) -> types.NestedArraySpec:
        return self._observation_spec

    def action_spec(self) -> types.NestedArraySpec:
        return self._action_spec

    def _step(self, action: types.NestedArray) -> ts.TimeStep:
        action = action[0]
        valid_moves = self._board.valid_moves()

        if valid_moves:
            i = round(action * len(valid_moves)) % len(valid_moves)
            pos = valid_moves[i]
            self._board.place(Color.black, pos)

        game_over, winner = self._board.check_game_over()
        reward = self._board.black.bit_count() - self._board.white.bit_count()
        self._board.black, self._board.white = self._board.white, self._board.black

        if game_over:
            return ts.termination(self._observe_board(), reward)

        return ts.transition(self._observe_board(), reward, discount=1)

    def _reset(self) -> ts.TimeStep:
        self._board = Board(init_turn_player_color=self._init_turn_player_color)
        return ts.restart(self._observe_board())
