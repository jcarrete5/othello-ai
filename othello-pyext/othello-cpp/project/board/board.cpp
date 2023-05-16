#include "board.h"

namespace othello {

std::optional<Color> GameBoard::at(const Position& p) const {
    if (white_.test(p))
        return Color::white;
    if (black_.test(p))
        return Color::black;
    return {};
}

void GameBoard::set(const Position& p, const Color c) {
    switch (c) {
    case Color::black:
        black_.set(p);
        white_.clear(p);
        break;
    case Color::white:
        white_.set(p);
        black_.clear(p);
        break;
    }
}

std::vector<Position> GameBoard::valid_moves(const Color c) const {
    BitBoard moves = (directional_valid_moves<right>(c) | directional_valid_moves<upright>(c) |
                      directional_valid_moves<up>(c) | directional_valid_moves<upleft>(c) |
                      directional_valid_moves<left>(c) | directional_valid_moves<downleft>(c) |
                      directional_valid_moves<down>(c) | directional_valid_moves<downright>(c));
    return moves.to_position_vector();
}

bool GameBoard::place_piece(Color c, const Position& p) {
    bool captured = capture(c, p);
    if (captured) {
        set(p, c);
    }
    return captured;
}

bool GameBoard::capture(const Color c, const Position& p) {
    bool valid_move = false;
    valid_move |= directional_capture<right>(c, p);
    valid_move |= directional_capture<upright>(c, p);
    valid_move |= directional_capture<up>(c, p);
    valid_move |= directional_capture<upleft>(c, p);
    valid_move |= directional_capture<left>(c, p);
    valid_move |= directional_capture<downleft>(c, p);
    valid_move |= directional_capture<down>(c, p);
    valid_move |= directional_capture<downright>(c, p);
    return valid_move;
}

template <>
const BitBoard& GameBoard::pieces<Color::white>() const {
    return white_;
}

template <>
const BitBoard& GameBoard::pieces<Color::black>() const {
    return black_;
}

template <>
const BitBoard& GameBoard::opposite_pieces<Color::white>() const {
    return black_;
}

template <>
const BitBoard& GameBoard::opposite_pieces<Color::black>() const {
    return white_;
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
