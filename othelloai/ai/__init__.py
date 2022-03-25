"""AI implementations for othello."""

import enum

from .minmax import MinmaxAIPlayer
from .random import RandomAIPlayer
from .minmax_cpp import MinmaxAIPlayerCPP


class AIOption(enum.Enum):
    """AI options."""

    Randy = enum.auto()
    Marty = enum.auto()
    CPP = enum.auto()


ai_default = AIOption.Randy
ai_options = {
    AIOption.Randy: RandomAIPlayer,
    AIOption.Marty: MinmaxAIPlayer,
    AIOption.CPP:   MinmaxAIPlayerCPP,
}
