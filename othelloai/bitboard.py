"""Bitboard operations. All operations assume that the board is 8x8."""

import operator as op
from collections import namedtuple
from functools import reduce

N_EDGE = 0xFF00000000000000
E_EDGE = 0x0101010101010101
S_EDGE = 0x00000000000000FF
W_EDGE = 0x8080808080808080
POS_SLOPE = 0x0102040810204080
NEG_SLOPE = 0x8040201008040201
ALL_ = 0xFFFFFFFFFFFFFFFF
NONE = 0x0000000000000000
DIRECTIONS = frozenset({"n", "ne", "e", "se", "s", "sw", "w", "nw"})

Position = namedtuple("Position", "row, col", module=__name__)


def pos_mask(row: int, col: int) -> int:
    """Return the bit mask for (row, col) on a bitboard."""
    assert 0 <= row < 8
    assert 0 <= col < 8
    return 0x8000000000000000 >> col >> row * 8


def shift(bits: int, dir_: str, times: int = 1) -> int:
    """Shift `bits` in direction `dir_` `times` times."""
    dir_ = dir_.lower()
    res = bits
    if "n" in dir_:
        res <<= 8 * times
    if "e" in dir_:
        # wall is a bit mask that ensures bits aren't shifted beyond where
        # they are meant to go
        wall = not_(reduce(op.or_, (W_EDGE >> shift_ for shift_ in range(times)), 0))
        res >>= 1 * times
        res &= wall
    if "s" in dir_:
        res >>= 8 * times
    if "w" in dir_:
        # wall is a bit mask that ensures bits aren't shifted beyond where
        # they are meant to go
        wall = not_(reduce(op.or_, (E_EDGE << shift_ for shift_ in range(times)), 0))
        res <<= 1 * times
        res &= wall
    return res & ALL_


def on_edge(bits: int) -> str:
    """Return the edges that contain on-bits."""
    edges = []
    if bits & N_EDGE:
        edges.append("n")
    if bits & E_EDGE:
        edges.append("e")
    if bits & S_EDGE:
        edges.append("s")
    if bits & W_EDGE:
        edges.append("w")
    return "".join(edges)


def dilate(bits: int, dir_: str, times: int = 1) -> int:
    """Set `times` bits in direction `dir_`."""
    for _ in range(times):
        bits |= shift(bits, dir_)
    return bits


def not_(bits: int) -> int:
    """Bitwise not of the bitboard."""
    # The `& ALL_` is necessary so python doesn't treat bits as 2's compliment
    return ~bits & ALL_


def to_list(bits: int) -> list[Position]:
    """Return a list of positions corresponding to the bits set in `bits`."""
    positions = []
    for r in range(8):
        for c in range(8):
            mask = pos_mask(r, c)
            if bits & mask > 0:
                positions.append(Position(r, c))
    return positions
