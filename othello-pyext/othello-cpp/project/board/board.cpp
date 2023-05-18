#include "board.h"

#include <sstream>

namespace othello {

std::optional<Color> GameBoard::at(const Position position) const
{
    if (white_.test(position))
        return Color::white;
    if (black_.test(position))
        return Color::black;
    return {};
}

void GameBoard::set_position(const Color color, const Position position)
{
    switch (color) {
    case Color::black:
        black_.set(position);
        white_.clear(position);
        break;
    case Color::white:
        white_.set(position);
        black_.clear(position);
        break;
    }
}

void GameBoard::set_bitboard_position(const Color color, const BitBoard position)
{
    switch (color) {
    case Color::black:
        black_.set(position);
        white_.clear(position);
        break;
    case Color::white:
        white_.set(position);
        black_.clear(position);
        break;
    }
}

template <>
const BitBoard& GameBoard::pieces<Color::white>() const
{
    return white_;
}

template <>
const BitBoard& GameBoard::pieces<Color::black>() const
{
    return black_;
}

template <>
const BitBoard& GameBoard::opposite_pieces<Color::white>() const
{
    return black_;
}

template <>
const BitBoard& GameBoard::opposite_pieces<Color::black>() const
{
    return white_;
}

std::string GameBoard::to_string() const
{
    std::stringstream ss;
    ss << *this;
    return ss.str();
}

std::ostream& operator<<(std::ostream& os, const GameBoard& board)
{
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

void display(const GameBoard& board)
{
    std::cout << board << std::endl;
}

std::set<Position> Game::valid_moves() const
{
    return valid_moves_bitboard().to_position_set();
}

BitBoard Game::valid_moves_bitboard() const
{
    const Color& color = active_color();
    BitBoard moves =
        (directional_valid_moves<Direction::right>(color) | directional_valid_moves<Direction::upright>(color) |
         directional_valid_moves<Direction::up>(color) | directional_valid_moves<Direction::upleft>(color) |
         directional_valid_moves<Direction::left>(color) | directional_valid_moves<Direction::downleft>(color) |
         directional_valid_moves<Direction::down>(color) | directional_valid_moves<Direction::downright>(color));
    return moves;
}

void Game::place_piece_bitboard_position(const BitBoard position)
{
    assert(position.count() == 1);
    directional_capture<Direction::right>(position);
    directional_capture<Direction::upright>(position);
    directional_capture<Direction::up>(position);
    directional_capture<Direction::upleft>(position);
    directional_capture<Direction::left>(position);
    directional_capture<Direction::downleft>(position);
    directional_capture<Direction::down>(position);
    directional_capture<Direction::downright>(position);
    board_.set_bitboard_position(active_color(), position);
    placed_piece_ = true;
    next_turn();
}

void Game::place_piece(const Position position)
{
    place_piece_bitboard_position(BitBoard{position});
}

} // namespace othello
