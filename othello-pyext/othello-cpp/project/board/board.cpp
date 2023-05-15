#include "board.h"

namespace othello {

template <>
const BitBoard& GameBoard::t_pieces_<Color::white>() const {
    return white;
}

template <>
const BitBoard& GameBoard::t_pieces_<Color::black>() const {
    return black;
}

template <>
const BitBoard& GameBoard::t_opposite_pieces_<Color::white>() const {
    return black;
}

template <>
const BitBoard& GameBoard::t_opposite_pieces_<Color::black>() const {
    return white;
}

std::ostream& operator<<(std::ostream& os, const GameBoard& board) {
    os << "\n";
    for (int row = 0; row < BitBoard::board_size; row++) {
        for (int col = 0; col < BitBoard::board_size; col++) {
            const auto c = board.at({row, col});
            if (!c.has_value()) {
                os << "#";
            } else {
                switch (*c) {
                case Color::white:
                    os << "W";
                    break;
                case Color::black:
                    os << "B";
                    break;
                }
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
