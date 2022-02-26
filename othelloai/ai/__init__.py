"""AI implementations for othello."""

import enum

from .minmax import MinmaxAIPlayer
from .random import RandomAIPlayer


class AIOption(enum.Enum):
    """AI options."""

    Randy = enum.auto()
    Marty = enum.auto()


ai_default = AIOption.Randy
ai_options = {
    AIOption.Randy: RandomAIPlayer,
    AIOption.Marty: MinmaxAIPlayer,
}
