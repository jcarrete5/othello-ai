#include "board.h"

namespace othello {
namespace bit_board {

template <>
bool on_edge<RIGHT>(const uint64_t& bits) {
    return bits & RIGHT_EDGE;
}
template <>
bool on_edge<UPRIGHT>(const uint64_t& bits) {
    return bits & (TOP_EDGE | RIGHT_EDGE);
}
template <>
bool on_edge<UP>(const uint64_t& bits) {
    return bits & TOP_EDGE;
}
template <>
bool on_edge<UPLEFT>(const uint64_t& bits) {
    return bits & (TOP_EDGE | LEFT_EDGE);
}
template <>
bool on_edge<LEFT>(const uint64_t& bits) {
    return bits & LEFT_EDGE;
}
template <>
bool on_edge<DOWNLEFT>(const uint64_t& bits) {
    return bits & (BOT_EDGE | LEFT_EDGE);
}
template <>
bool on_edge<DOWN>(const uint64_t& bits) {
    return bits & BOT_EDGE;
}
template <>
bool on_edge<DOWNRIGHT>(const uint64_t& bits) {
    return bits & (BOT_EDGE | RIGHT_EDGE);
}

template <>
uint64_t shift<UP>(const uint64_t& bits, const size_t& n) {
    return bits << (8 * n);
}
template <>
uint64_t shift<DOWN>(const uint64_t& bits, const size_t& n) {
    return bits >> (8 * n);
}
template <>
uint64_t shift<RIGHT>(const uint64_t& bits, const size_t& n) {
    uint64_t shifted = bits;
    uint64_t wall    = 0;
    for (int i = 0; i < n; i++)
        wall |= (LEFT_EDGE >> i);
    wall = ~wall;
    shifted >>= (1 * n);
    shifted &= wall;
    return shifted;
}
template <>
uint64_t shift<LEFT>(const uint64_t& bits, const size_t& n) {
    uint64_t shifted = bits;
    uint64_t wall    = 0;
    for (int i = 0; i < n; i++)
        wall |= (RIGHT_EDGE << i);
    wall = ~wall;
    shifted <<= (1 * n);
    shifted &= wall;
    return shifted;
}
template <>
uint64_t shift<UPRIGHT>(const uint64_t& bits, const size_t& n) {
    return shift<RIGHT>(shift<UP>(bits,n), n);
}
template <>
uint64_t shift<UPLEFT>(const uint64_t& bits, const size_t& n) {
    return shift<LEFT>(shift<UP>(bits,n), n);
}
template <>
uint64_t shift<DOWNLEFT>(const uint64_t& bits, const size_t& n) {
    return shift<LEFT>(shift<DOWN>(bits,n), n);
}
template <>
uint64_t shift<DOWNRIGHT>(const uint64_t& bits, const size_t& n) {
    return shift<RIGHT>(shift<DOWN>(bits,n), n);
}

std::vector<Position> to_positions(const uint64_t& bits) {
    std::vector<Position> positions;
    for (size_t row = 0; row < 8; row++) {
        for (size_t col = 0; col < 8; col++) {
            Position p{row, col};
            if (position_mask(p) & bits)
                positions.push_back(p);
        }
    }
    return positions;
}

} // namespace bit_board

std::ostream& operator<<(std::ostream& os, const GameBoard& board) {
    os << "\n";
    Position p;
    for (size_t row = 0; row < 8; row++) {
        for (size_t col = 0; col < 8; col++) {
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

} // namespace othello
