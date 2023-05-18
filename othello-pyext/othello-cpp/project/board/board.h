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
    [[nodiscard]] std::optional<Color> at(Position position) const;
    void set_position(Color color, Position position);
    void set_bitboard_position(Color color, BitBoard position);
    void clear_position(const Position position)
    {
        white_.clear(position);
        black_.clear(position);
    }
    void clear_bitboard_position(const BitBoard position)
    {
        assert(position.count() == 1);
        white_.clear(position);
        black_.clear(position);
    }
    void clear_all()
    {
        white_.clear_all();
        black_.clear_all();
    }

    [[nodiscard]] std::size_t white_count() const
    {
        return white_.count();
    }
    [[nodiscard]] std::size_t black_count() const
    {
        return black_.count();
    }
    [[nodiscard]] std::size_t color_count(const Color color) const
    {
        return pieces(color).count();
    }

    [[nodiscard]] std::vector<Position> white_positions() const
    {
        return white_.to_position_vector();
    }
    [[nodiscard]] std::vector<Position> black_positions() const
    {
        return black_.to_position_vector();
    }

    friend std::ostream& operator<<(std::ostream& os, const GameBoard& board);
    [[nodiscard]] std::string to_string() const;

  private:
    BitBoard white_;
    BitBoard black_;

    template <Color C>
    [[nodiscard]] const BitBoard& pieces() const;
    template <Color C>
    [[nodiscard]] const BitBoard& opposite_pieces() const;

    BitBoard& pieces(const Color color)
    {
        return (color == Color::white) ? white_ : black_;
    }
    [[nodiscard]] const BitBoard& pieces(const Color color) const
    {
        return (color == Color::white) ? white_ : black_;
    }
    BitBoard& opposite_pieces(const Color color)
    {
        return pieces(get_opposite_color(color));
    }
    [[nodiscard]] const BitBoard& opposite_pieces(const Color color) const
    {
        return pieces(get_opposite_color(color));
    }

    [[nodiscard]] BitBoard vacant() const
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
        board_.set_position(Color::white, {3, 3});
        board_.set_position(Color::white, {4, 4});
        board_.set_position(Color::black, {4, 3});
        board_.set_position(Color::black, {3, 4});
    }

    [[nodiscard]] Color active_color() const
    {
        return active_color_;
    }

    [[nodiscard]] const GameBoard& board() const
    {
        return board_;
    }

    [[nodiscard]] bool has_valid_move() const
    {
        return !valid_moves_bitboard().empty();
    }
    [[nodiscard]] bool is_valid_move(const Position position) const
    {
        if (position.x() < 0 || position.x() >= BitBoard::board_size || position.y() < 0 || position.y() >= BitBoard::board_size) {
            return false;
        }
        return valid_moves_bitboard().test(position);
    }
    [[nodiscard]] std::set<Position> valid_moves() const;
    [[nodiscard]] BitBoard valid_moves_bitboard() const;

    void place_piece(Position position);
    void place_piece_bitboard_position(BitBoard position);
    void skip_turn() {
        next_turn();
    }
    [[nodiscard]] bool is_game_over() const
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
    [[nodiscard]] BitBoard directional_valid_moves(Color color) const;

    template <Direction D>
    void directional_capture(BitBoard position);

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

};

template <Direction D>
BitBoard Game::directional_valid_moves(const Color color) const
{
    BitBoard moves{0};
    BitBoard candidates{board_.opposite_pieces(color) & BitBoard::shift<D>(board_.pieces(color))};
    while (!candidates.empty()) {
        const auto shifted = BitBoard::shift<D>(candidates);
        moves |= board_.vacant() & shifted;
        candidates = board_.opposite_pieces(color) & shifted;
    }
    return moves;
}

template <Direction D>
void Game::directional_capture(const BitBoard position)
{
    assert(position.count() == 1);
    const Color color = active_color();
    State<D> state{color, board_, position};
    while (state.should_keep_dilating()) {
        state.dilate();
    }
    if (state.should_commit()) {
        board_.pieces(color).set(state.bits());
        board_.opposite_pieces(color).clear(state.bits());
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
    [[nodiscard]] bool should_commit() const;
    bool should_keep_dilating();
    [[nodiscard]] const BitBoard& bits() const;

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
    BitBoard selected = ~start_ & bits_;
    on_edge_ = bits_.on_edge<D>();
    capped_ = my_pieces_.test_any(selected);
    on_empty_ = vacant_.test_any(selected);
    return !(on_edge_ || capped_ || on_empty_);
}

template <Direction D>
const BitBoard& Game::State<D>::bits() const
{
    return bits_;
}

} // namespace othello
