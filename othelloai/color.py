"""Player colors."""

import enum


class Color(enum.Enum):
    """Represents the color of the pieces a player controls."""

    black = enum.auto()
    white = enum.auto()


def opposite_color(c: Color) -> Color:
    """Return the color opposite to that of the input."""
    return Color.white if c is Color.black else Color.black
