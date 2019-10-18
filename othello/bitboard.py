"""
Bitboard operations. Assumes the board is 8x8.
"""
from typing import TypeVar, List
from collections import namedtuple

n_edge = 0xff00000000000000
e_edge = 0x0101010101010101
s_edge = 0x00000000000000ff
w_edge = 0x8080808080808080
pos_slope = 0x0102040810204080
neg_slope = 0x8040201008040201
all_ = 0xffffffffffffffff
none = 0x0000000000000000
directions = {'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'}

Position = namedtuple('Position', 'row, col', module=__name__)

def pos_mask(row: int, col: int) -> int:
    """ Return the bit mask for (row, col) on a bitboard. """
    assert 0 <= row < 8
    assert 0 <= col < 8
    return 0x8000000000000000 >> col >> row * 8

def shift(bits: int, dir_: str, times: int=1) -> int:
    """ Shift `bits` in direction `dir_` `times` times. """
    dir_ = dir_.lower()
    res = bits
    if 'n' in dir_:
        res <<= 8 * times
    if 'e' in dir_:
        res >>= 1 * times
    if 's' in dir_:
        res >>= 8 * times
    if 'w' in dir_:
        res <<= 1 * times
    return res & all_

def on_edge(bits: int) -> str:
    """ Returns the edges that contain on-bits. """
    edges = []
    if bits & n_edge:
        edges.append('n')
    if bits & e_edge:
        edges.append('e')
    if bits & s_edge:
        edges.append('s')
    if bits & w_edge:
        edges.append('w')
    return ''.join(edges)

def dilate(bits: int, dir_: str, times: int=1) -> int:
    return bits | shift(bits, dir_, times)

def not_(bits: int) -> int:
    return ~bits & all_

def to_list(bits: int) -> List[Position]:
    pass