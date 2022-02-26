"""AI implementations for othello."""

from .random import RandomAIPlayer
from .minmax import MinmaxAIPlayer

ai_default = "Randy"
ai_options = {"Randy": RandomAIPlayer, "Marty": MinmaxAIPlayer}
