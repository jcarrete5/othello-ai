#include "board.h"

#include <sstream>

namespace othello {

std::optional<Color> GameBoard::at(const Position p) const
{
    if (white_.test(p))
        return Color::white;
    if (black_.test(p))
        return Color::black;
    return {};
}

void GameBoard::set(const Color c, const Position p)
{
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

void GameBoard::set(const Color c, const BitBoard p)
{
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
    const Color& c = active_color();
    BitBoard moves =
        (directional_valid_moves<Direction::right>(c) | directional_valid_moves<Direction::upright>(c) |
         directional_valid_moves<Direction::up>(c) | directional_valid_moves<Direction::upleft>(c) |
         directional_valid_moves<Direction::left>(c) | directional_valid_moves<Direction::downleft>(c) |
         directional_valid_moves<Direction::down>(c) | directional_valid_moves<Direction::downright>(c));
    return moves;
}

void Game::place_piece(const BitBoard p)
{
    directional_capture<Direction::right>(p);
    directional_capture<Direction::upright>(p);
    directional_capture<Direction::up>(p);
    directional_capture<Direction::upleft>(p);
    directional_capture<Direction::left>(p);
    directional_capture<Direction::downleft>(p);
    directional_capture<Direction::down>(p);
    directional_capture<Direction::downright>(p);
    board_.set(active_color(), p);
    placed_piece_ = true;
}

void Game::place_piece(const Position p)
{
    place_piece(BitBoard{p});
}

} // namespace othello
