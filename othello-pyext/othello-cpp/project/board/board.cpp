#include "board.h"

#include <sstream>

namespace othello {

std::optional<Color> GameBoard::at(const Position& p) const {
    if (white_.test(p))
        return Color::white;
    if (black_.test(p))
        return Color::black;
    return {};
}

void GameBoard::set(const Color c, const Position& p) {
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

std::string GameBoard::to_string() const {
    std::stringstream ss;
    ss << *this;
    return ss.str();
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

std::set<Position> Game::valid_moves() const {
    const Color c = active_color();
    BitBoard moves = (directional_valid_moves<right>(c) | directional_valid_moves<upright>(c) |
                      directional_valid_moves<up>(c) | directional_valid_moves<upleft>(c) |
                      directional_valid_moves<left>(c) | directional_valid_moves<downleft>(c) |
                      directional_valid_moves<down>(c) | directional_valid_moves<downright>(c));
    return moves.to_position_set();
}

void Game::place_piece(const Position& p) {
    if (!is_valid_move(p)) {
        throw std::invalid_argument{"invalid move"};
    }
    directional_capture<right>(p);
    directional_capture<upright>(p);
    directional_capture<up>(p);
    directional_capture<upleft>(p);
    directional_capture<left>(p);
    directional_capture<downleft>(p);
    directional_capture<down>(p);
    directional_capture<downright>(p);
    board_.set(active_color(), p);

    active_color_ = get_opposite_color(active_color());
}

} // namespace othello
