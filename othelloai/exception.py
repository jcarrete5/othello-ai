"""General exception definitions."""


class IllegalMoveError(Exception):
    """Raised when an illegal move is attempted."""


class PassMove(Exception):
    """Raised when a player passes their move."""


class PlayerInterrupted(Exception):
    """Raised when a player is interrupted while making a move."""
