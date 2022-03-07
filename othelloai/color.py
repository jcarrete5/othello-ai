"""Player colors."""

import enum


class Color(enum.Enum):
    """Represents the color of the pieces a player controls."""

    black = 1
    white = 2


def opposite_color(c: Color) -> Color:
    """Return the color opposite to that of the input."""
    return Color.white if c is Color.black else Color.black
