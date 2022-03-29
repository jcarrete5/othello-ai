"""Board implementation and manipulation."""

import re
from copy import copy

from . import bitboard as bb
from .color import Color
from .exception import IllegalMoveError


class Board:
    """A board that can be manipulated adhering to the rules of othello."""

    def __init__(
        self,
        init_white=0x0000001008000000,
        init_black=0x0000000810000000,
        init_turn_player_color=Color.black,
    ):
        """Construct a board with initial white and black pieces and turn player."""
        self.white = init_white
        self.black = init_black
        self.turn_player_color = init_turn_player_color

    def swap_turn_players(self):
        """Swap current turn player."""
        if self.turn_player_color is Color.black:
            self.turn_player_color = Color.white
        else:
            self.turn_player_color = Color.black

    def empty_cells(self) -> int:
        """Return a bitboard representing empty cells."""
        return bb.not_(self.white | self.black)

    def valid_moves(self) -> list[bb.Position]:
        """Return a list of positions of valid moves for the turn player."""
        if self.turn_player_color is Color.black:
            my_pieces = self.black
            foe_pieces = self.white
        else:
            my_pieces = self.white
            foe_pieces = self.black
        moves_bb = 0x0
        for dir_ in bb.DIRECTIONS:
            candidates = foe_pieces & bb.shift(my_pieces, dir_)
            while candidates != 0:
                shifted = bb.shift(candidates, dir_)
                moves_bb |= self.empty_cells() & shifted
                candidates = foe_pieces & shifted
        return bb.to_list(moves_bb)

    def place(self, color: Color, pos: bb.Position):
        """Place a piece of color `color` at position `pos`.

        Raises an IllegalMoveError if an illegal move was attempted
        """
        assert 0 <= pos.row < 8
        assert 0 <= pos.col < 8
        pos_mask = bb.pos_mask(*pos)
        self._capture(color, pos)
        if color is Color.black:
            self.black |= pos_mask
        else:
            self.white |= pos_mask

    def _capture(self, color: Color, pos: bb.Position):
        """Find pieces that should be captured.

        It does this by playing `color` at `pos` and capture those pieces.
        Raises an IllegalMoveError if an illegal move was attempted.
        """
        my_pieces = self.white if color is Color.white else self.black
        empty = self.empty_cells()

        class State:
            def __init__(self, dir_, init_bb=0x0):
                self.bb = init_bb
                self.dir = dir_
                self.capped = False
                self.on_edge = False
                self.on_empty = False

            def dilate(self):
                self.bb = bb.dilate(self.bb, self.dir)

            def should_commit(self):
                return self.capped

            def should_keep_dilating(self):
                selected = bb.not_(bb.pos_mask(*pos)) & self.bb
                self.on_edge = len(set(self.dir) & set(bb.on_edge(self.bb))) > 0
                self.capped = my_pieces & selected != 0
                self.on_empty = empty & selected != 0
                return not self.on_edge and not self.capped and not self.on_empty

        start = bb.pos_mask(*pos)
        states = [State(dir_, start) for dir_ in bb.DIRECTIONS]
        did_commit = False
        for state in states:
            while state.should_keep_dilating():
                state.dilate()
            if state.should_commit():
                did_commit = True
                if color is Color.white:
                    self.white |= state.bb
                    self.black &= bb.not_(state.bb)
                elif color is Color.black:
                    self.black |= state.bb
                    self.white &= bb.not_(state.bb)
        if not did_commit:
            raise IllegalMoveError

    def copy(self):
        """Return a shallow copy of this board."""
        return copy(self)

    def __eq__(self, other: "Board"):
        return (
            self.white == other.white
            and self.black == other.black
            and self.turn_player_color == other.turn_player_color
        )

    def __str__(self):
        def symbol_at(row: int, col: int) -> str:
            mask = bb.pos_mask(row, col)
            if self.white & mask != 0:
                return "\u2588"
            elif self.black & mask != 0:
                return "\u2591"
            else:
                return "-"

        res = [symbol_at(r, c) for r in range(8) for c in range(8)]
        return "\n".join(re.findall("........", "".join(res)))
