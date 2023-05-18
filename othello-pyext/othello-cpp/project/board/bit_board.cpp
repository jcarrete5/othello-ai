#include "bit_board.h"

#include <bit>
#include <cassert>
#include <exception>
#include <set>
#include <vector>

BitBoard::BitBoard(const std::string& board)
{
    if (board.length() != n_bits) {
        throw std::runtime_error("invalid string length for BitBoard");
    }

    for (size_t i = 0; i < board.length(); ++i) {
        if (board[i] == '1') {
            bits_ |= (top_left >> i);
        }
    }
}

template <>
bool BitBoard::on_edge<Direction::right>() const
{
    return test_any(make_right_edge());
}

template <>
bool BitBoard::on_edge<Direction::upright>() const
{
    return test_any(make_top_right_edge());
}

template <>
bool BitBoard::on_edge<Direction::up>() const
{
    return test_any(make_top_edge());
}

template <>
bool BitBoard::on_edge<Direction::upleft>() const
{
    return test_any(make_top_left_edge());
}

template <>
bool BitBoard::on_edge<Direction::left>() const
{
    return test_any(make_left_edge());
}

template <>
bool BitBoard::on_edge<Direction::downright>() const
{
    return test_any(make_bottom_right_edge());
}

template <>
bool BitBoard::on_edge<Direction::down>() const
{
    return test_any(make_bottom_edge());
}

template <>
bool BitBoard::on_edge<Direction::downleft>() const
{
    return test_any(make_bottom_left_edge());
}

bool BitBoard::on_edge(const Direction direction) const
{
    switch (direction) {
    case Direction::right:
        return on_edge<Direction::right>();
    case Direction::upright:
        return on_edge<Direction::upright>();
    case Direction::up:
        return on_edge<Direction::up>();
    case Direction::upleft:
        return on_edge<Direction::upleft>();
    case Direction::left:
        return on_edge<Direction::left>();
    case Direction::downleft:
        return on_edge<Direction::downleft>();
    case Direction::down:
        return on_edge<Direction::down>();
    case Direction::downright:
        return on_edge<Direction::downright>();
    default:
        assert(!"invalid direction");
        return {};
    }
}

bool BitBoard::on_any_edge() const
{
    return test_any(make_all_edge());
}

bool BitBoard::on_any_corner() const
{
    return test_any(make_all_corners());
}

BitBoard BitBoard::shift(BitBoard board, const Direction direction, const size_t n)
{
    return board.shift_assign(direction, n);
}

BitBoard& BitBoard::dilate(const Direction direction, const size_t n)
{
    switch (direction) {
    case Direction::right:
        return dilate<Direction::right>(n);
    case Direction::upright:
        return dilate<Direction::upright>(n);
    case Direction::up:
        return dilate<Direction::up>(n);
    case Direction::upleft:
        return dilate<Direction::upleft>(n);
    case Direction::left:
        return dilate<Direction::left>(n);
    case Direction::downleft:
        return dilate<Direction::downleft>(n);
    case Direction::down:
        return dilate<Direction::down>(n);
    case Direction::downright:
        return dilate<Direction::downright>(n);
    }
    assert(!"invalid direction");
    return *this;
}

template <>
BitBoard& BitBoard::shift_assign<Direction::up>(const size_t n)
{
    bits_ <<= (board_size * n);
    return *this;
}
template <>
BitBoard& BitBoard::shift_assign<Direction::down>(const size_t n)
{
    bits_ >>= (board_size * n);
    return *this;
}
template <>
BitBoard& BitBoard::shift_assign<Direction::left>(const size_t n)
{
    Bits wall{0};
    for (size_t i = 0; i < n; i++) {
        wall |= (right_edge << i);
    }
    bits_ <<= n;
    bits_ &= ~wall;
    return *this;
}
template <>
BitBoard& BitBoard::shift_assign<Direction::right>(const size_t n)
{
    Bits wall{0};
    for (size_t i = 0; i < n; i++) {
        wall |= (left_edge >> i);
    }
    bits_ >>= n;
    bits_ &= ~wall;
    return *this;
}
template <>
BitBoard& BitBoard::shift_assign<Direction::upright>(const size_t n)
{
    return shift_assign<Direction::up>(n).shift_assign<Direction::right>(n);
}
template <>
BitBoard& BitBoard::shift_assign<Direction::upleft>(const size_t n)
{
    return shift_assign<Direction::up>(n).shift_assign<Direction::left>(n);
}
template <>
BitBoard& BitBoard::shift_assign<Direction::downright>(const size_t n)
{
    return shift_assign<Direction::down>(n).shift_assign<Direction::right>(n);
}
template <>
BitBoard& BitBoard::shift_assign<Direction::downleft>(const size_t n)
{
    return shift_assign<Direction::down>(n).shift_assign<Direction::left>(n);
}

BitBoard& BitBoard::shift_assign(const Direction direction, const size_t n)
{
    switch (direction) {
    case Direction::right:
        return shift_assign<Direction::right>(n);
    case Direction::upright:
        return shift_assign<Direction::upright>(n);
    case Direction::up:
        return shift_assign<Direction::up>(n);
    case Direction::upleft:
        return shift_assign<Direction::upleft>(n);
    case Direction::left:
        return shift_assign<Direction::left>(n);
    case Direction::downleft:
        return shift_assign<Direction::downleft>(n);
    case Direction::down:
        return shift_assign<Direction::down>(n);
    case Direction::downright:
        return shift_assign<Direction::downright>(n);
    }
    assert(!"invalid direction");
    return *this;
}

BitBoard& BitBoard::shift_assign(const BitBoard::Position relative_offset)
{
    if (relative_offset.x() >= 0) {
        shift_assign<Direction::down>(relative_offset.x());
    } else {
        shift_assign<Direction::up>(-relative_offset.x());
    }
    if (relative_offset.y() >= 0) {
        shift_assign<Direction::right>(relative_offset.y());
    } else {
        shift_assign<Direction::left>(-relative_offset.y());
    }
    return *this;
}

BitBoard BitBoard::neighbors_cardinal(const Position position)
{
    auto board = BitBoard{position};
    return shift<Direction::right>(board) | shift<Direction::up>(board) | shift<Direction::left>(board) |
           shift<Direction::down>(board);
}

BitBoard BitBoard::neighbors_diagonal(const Position position)
{
    auto board = BitBoard{position};
    return shift<Direction::upright>(board) | shift<Direction::upleft>(board) | shift<Direction::downleft>(board) |
           shift<Direction::downright>(board);
}

BitBoard BitBoard::neighbors_cardinal_and_diagonal(const Position position)
{
    return neighbors_cardinal(position) | neighbors_diagonal(position);
}

std::size_t BitBoard::count() const
{
    return std::popcount(bits_);
}

BitBoard::Position BitBoard::to_position() const
{
    return index_to_position(std::countl_zero(bits_));
}

std::vector<BitBoard> BitBoard::to_bitboard_position_vector() const
{
    std::vector<BitBoard> positions;
    positions.reserve(n_bits);
    for (BitBoard position{top_left}; position != BitBoard{0U}; position >>= 1) {
        if (test_any(position)) {
            positions.push_back(position);
        }
    }
    return positions;
}

std::vector<BitBoard::Position> BitBoard::to_position_vector() const
{
    std::vector<Position> positions;
    for (int column = 0; column < board_size; column++) {
        for (int row = 0; row < board_size; row++) {
            Position position{row, column};
            if (test(position)) {
                positions.push_back(position);
            }
        }
    }
    return positions;
}

std::set<BitBoard> BitBoard::to_bitboard_position_set() const
{
    std::set<BitBoard> positions;
    for (BitBoard position{top_left}; position != BitBoard{0U}; position >>= 1) {
        if (test_any(position)) {
            positions.insert(position);
        }
    }
    return positions;
}

std::set<BitBoard::Position> BitBoard::to_position_set() const
{
    std::set<Position> positions;
    for (int column = 0; column < board_size; column++) {
        for (int row = 0; row < board_size; row++) {
            Position position{row, column};
            if (test(position)) {
                positions.insert(position);
            }
        }
    }
    return positions;
}

std::string BitBoard::to_string() const
{
    std::string str;
    for (size_t i = 0; i < n_bits; ++i) {
        str.push_back(((bits_ & (top_left >> i)) == 0U) ? '0' : '1');
    }
    return str;
}
