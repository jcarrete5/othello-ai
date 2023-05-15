#include "board.h"

namespace othello {

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
    GameBoard::Position p;
    for (size_t row = 0; row < BitBoard::board_size; row++) {
        for (size_t col = 0; col < BitBoard::board_size; col++) {
            p.x()   = row;
            p.y()   = col;
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
