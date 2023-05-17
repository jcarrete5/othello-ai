#pragma once

#include "bit_board.h"

#include <cstddef>

#include <array>
#include <bitset>
#include <iostream>
#include <optional>
#include <set>
#include <string>
#include <vector>

namespace othello {

enum class Color
{
    black,
    white,
};

template <Color C>
struct opposite_color
{
    static const Color value;
};

template <>
inline const Color opposite_color<Color::white>::value = Color::black;

template <>
inline const Color opposite_color<Color::black>::value = Color::white;

template <Color C>
using opposite_color_v = opposite_color<C>::value;

inline Color get_opposite_color(const Color color)
{
    switch (color) {
    case Color::black:
        return Color::white;
    case Color::white:
        return Color::black;
    }
}

using Position = BitBoard::Position;

class GameBoard
{
    friend class Game;

  public:
    GameBoard() {}

    std::optional<Color> at(Position p) const;
    void set(Color c, Position p);
    void set(Color c, BitBoard p);
    void clear(const Position p)
    {
        white_.clear(p);
        black_.clear(p);
    }
    void clear(const BitBoard p)
    {
        white_.clear(p);
        black_.clear(p);
    }
    void clear_all()
    {
        white_.clear_all();
        black_.clear_all();
    }

    std::size_t white_count() const
    {
        return white_.count();
    }
    std::size_t black_count() const
    {
        return black_.count();
    }
    std::size_t color_count(const Color c) const
    {
        return pieces(c).count();
    }

    std::vector<Position> white_positions() const
    {
        return white_.to_position_vector();
    }
    std::vector<Position> black_positions() const
    {
        return black_.to_position_vector();
    }

    friend std::ostream& operator<<(std::ostream& os, const GameBoard& board);
    std::string to_string() const;

  private:
    BitBoard white_;
    BitBoard black_;

    template <Color C>
    const BitBoard& pieces() const;
    template <Color C>
    const BitBoard& opposite_pieces() const;

    BitBoard& pieces(const Color c)
    {
        return (c == Color::white) ? white_ : black_;
    }
    const BitBoard& pieces(const Color c) const
    {
        return (c == Color::white) ? white_ : black_;
    }
    BitBoard& opposite_pieces(const Color c)
    {
        return pieces(get_opposite_color(c));
    }
    const BitBoard& opposite_pieces(const Color c) const
    {
        return pieces(get_opposite_color(c));
    }

    BitBoard vacant() const
    {
        return ~(white_ | black_);
    }
};

class Game
{
  public:
    Game()
    {
        reset();
    }

    Game(const GameBoard& board, const Color active_color) : board_{board}, active_color_{active_color} {}

    void set_up()
    {
        board_.clear_all();
        board_.set(Color::white, {3, 3});
        board_.set(Color::white, {4, 4});
        board_.set(Color::black, {4, 3});
        board_.set(Color::black, {3, 4});
    }

    Color active_color() const
    {
        return active_color_;
    }

    const GameBoard& board() const
    {
        return board_;
    }

    bool has_valid_move() const
    {
        return !valid_moves_bitboard().empty();
    }
    std::set<Position> valid_moves() const;
    BitBoard valid_moves_bitboard() const;

    void place_piece(Position p);
    void place_piece(BitBoard p);
    void next_turn()
    {
        active_color_ = get_opposite_color(active_color());
        if (!placed_piece_) {
            ++pass_count_;
        } else {
            pass_count_ = 0;
            placed_piece_ = false;
        }
    }

    bool is_game_over()
    {
        return pass_count_ == 2;
    }

    void reset()
    {
        set_up();
        active_color_ = Color::black;
    }

  private:
    GameBoard board_;
    Color active_color_;
    int pass_count_ = 0;
    bool placed_piece_ = false;

    template <Direction D>
    class State;

    template <Direction D>
    BitBoard directional_valid_moves(Color c) const;

    template <Direction D>
    void directional_capture(BitBoard p);
};

template <Direction D>
BitBoard Game::directional_valid_moves(const Color c) const
{
    BitBoard moves;
    BitBoard candidates{board_.opposite_pieces(c) & BitBoard::shift<D>(board_.pieces(c))};
    while (!candidates.empty()) {
        const auto shifted = BitBoard::shift<D>(candidates);
        moves |= board_.vacant() & shifted;
        candidates = board_.opposite_pieces(c) & shifted;
    }
    return moves;
}

template <Direction D>
void Game::directional_capture(const BitBoard p)
{
    const Color c = active_color();
    State<D> s{c, board_, p};
    while (s.should_keep_dilating()) {
        s.dilate();
    }
    if (s.should_commit()) {
        board_.pieces(c).set(s.bits());
        board_.opposite_pieces(c).clear(s.bits());
    }
}

template <Direction D>
class Game::State
{
  public:
    State(const Color color, GameBoard& board, const BitBoard start)
        : my_pieces_(board.pieces(color)), vacant_(board.vacant()), start_{start}, bits_{start}
    {}

    void dilate();
    bool should_commit() const;
    bool should_keep_dilating();
    const BitBoard& bits() const;

  private:
    BitBoard start_;
    BitBoard my_pieces_;
    BitBoard vacant_;

    BitBoard bits_;
    bool capped_;
    bool on_edge_;
    bool on_empty_;
};

template <Direction D>
void Game::State<D>::dilate()
{
    bits_ = bits_.dilate<D>();
}

template <Direction D>
bool Game::State<D>::should_commit() const
{
    return capped_;
}

template <Direction D>
bool Game::State<D>::should_keep_dilating()
{
    BitBoard selected_ = ~start_ & bits_;
    on_edge_ = bits_.on_edge<D>();
    capped_ = my_pieces_.test_any(selected_);
    on_empty_ = vacant_.test_any(selected_);
    return !(on_edge_ || capped_ || on_empty_);
}

template <Direction D>
const BitBoard& Game::State<D>::bits() const
{
    return bits_;
}

} // namespace othello
