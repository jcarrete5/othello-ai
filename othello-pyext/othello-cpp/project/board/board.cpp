#include "board.h"

namespace othello {

Position operator+(const Position& lhs, const Position& rhs) {
    return Position{lhs.row + rhs.row, lhs.col + rhs.col};
}
Position operator-(const Position& lhs, const Position& rhs) {
    return Position{lhs.row - rhs.row, lhs.col - rhs.col};
}
bool operator==(const Position& lhs, const Position& rhs) {
    return (lhs.row == rhs.row && lhs.col == rhs.col);
}

template <>
bool BitBoard::on_edge<RIGHT>() const {
    return bits & RIGHT_EDGE;
}
template <>
bool BitBoard::on_edge<UPRIGHT>() const {
    return bits & (TOP_EDGE | RIGHT_EDGE);
}
template <>
bool BitBoard::on_edge<UP>() const {
    return bits & TOP_EDGE;
}
template <>
bool BitBoard::on_edge<UPLEFT>() const {
    return bits & (TOP_EDGE | LEFT_EDGE);
}
template <>
bool BitBoard::on_edge<LEFT>() const {
    return bits & LEFT_EDGE;
}
template <>
bool BitBoard::on_edge<DOWNRIGHT>() const {
    return bits & (BOT_EDGE | RIGHT_EDGE);
}
template <>
bool BitBoard::on_edge<DOWN>() const {
    return bits & BOT_EDGE;
}
template <>
bool BitBoard::on_edge<DOWNLEFT>() const {
    return bits & (BOT_EDGE | LEFT_EDGE);
}
template <>
BitBoard BitBoard::shift<UP>(const size_t& n) const {
    return bits << (N * n);
}
template <>
BitBoard BitBoard::shift<DOWN>(const size_t& n) const {
    return bits >> (N * n);
}
template <>
BitBoard BitBoard::shift<RIGHT>(const size_t& n) const {
    BitBoard shifted{bits};
    bits_type wall{0};
    for (int i = 0; i < n; i++)
        wall |= (LEFT_EDGE >> i);
    wall = ~wall;
    shifted >>= (1 * n);
    shifted &= wall;
    return shifted;
}
template <>
BitBoard BitBoard::shift<LEFT>(const size_t& n) const {
    BitBoard shifted{bits};
    bits_type wall{0};
    for (int i = 0; i < n; i++)
        wall |= (RIGHT_EDGE << i);
    wall = ~wall;
    shifted <<= (1 * n);
    shifted &= wall;
    return shifted;
}
template <>
BitBoard BitBoard::shift<UPRIGHT>(const size_t& n) const {
    return shift<UP>(n).shift<RIGHT>(n);
}
template <>
BitBoard BitBoard::shift<UPLEFT>(const size_t& n) const {
    return shift<UP>(n).shift<LEFT>(n);
}
template <>
BitBoard BitBoard::shift<DOWNLEFT>(const size_t& n) const {
    return shift<DOWN>(n).shift<LEFT>(n);
}
template <>
BitBoard BitBoard::shift<DOWNRIGHT>(const size_t& n) const {
    return shift<DOWN>(n).shift<RIGHT>(n);
}

std::vector<Position> BitBoard::to_positions() const {
    std::vector<Position> positions;
    for (size_t row = 0; row < N; row++) {
        for (size_t col = 0; col < N; col++) {
            Position p{row, col};
            if (position_mask(p) & bits)
                positions.push_back(p);
        }
    }
    return positions;
}

std::bitset<BitBoard::N * BitBoard::N> BitBoard::to_bitset() const {
    return std::bitset<N * N>{bits};
}


template <>
const BitBoard& GameBoard::t_pieces_<WHITE>() const {
    return white;
}

template <>
const BitBoard& GameBoard::t_pieces_<BLACK>() const {
    return black;
}

template <>
const BitBoard& GameBoard::t_opposite_pieces_<WHITE>() const {
    return black;
}

template <>
const BitBoard& GameBoard::t_opposite_pieces_<BLACK>() const {
    return white;
}


std::ostream& operator<<(std::ostream& os, const GameBoard& board) {
    os << "\n";
    Position p;
    for (size_t row = 0; row < BitBoard::N; row++) {
        for (size_t col = 0; col < BitBoard::N; col++) {
            p.row   = row;
            p.col   = col;
            Color c = board.at(p);
            switch (c) {
            case NONE:
                os << "#";
                break;
            case WHITE:
                os << "W";
                break;
            case BLACK:
                os << "B";
                break;
            case MAX_COLOR:
                os << "X";
                break;
            default:
                os << "X";
                break;
            }
        }
        os << "\n";
    }
    return os;
}

void display(const GameBoard& board) {
    std::cout << board << std::endl;
}

} // namespace othello
