"""AI implementations for othello."""

from .random import RandomAIPlayer
from .minmax import MinmaxAIPlayer

ai_default = "Random"
ai_options = {"Random": RandomAIPlayer, "Marty": MinmaxAIPlayer}
