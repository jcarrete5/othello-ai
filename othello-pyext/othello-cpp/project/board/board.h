#pragma once

#include "bit_board.h"

#include <cstddef>

#include <array>
#include <bitset>
#include <iostream>
#include <optional>
#include <string>
#include <vector>

namespace othello {

enum class Color {
    black,
    white,
};

template <Color C>
struct opposite_color {
    static const Color value;
};

template <>
inline const Color opposite_color<Color::white>::value = Color::black;

template <>
inline const Color opposite_color<Color::black>::value = Color::white;

template <Color C>
using opposite_color_v = opposite_color<C>::value;

inline Color get_opposite_color(const Color color) {
    switch (color) {
    case Color::black:
        return Color::white;
    case Color::white:
        return Color::black;
    }
}

using Position = BitBoard::Position;

class GameBoard {
  public:
    GameBoard() {
        set_up();
    }

    void clear_all() {
        white_.clear_all();
        black_.clear_all();
    }

    void set_up() {
        clear_all();
        white_.set({3, 3});
        white_.set({4, 4});
        black_.set({4, 3});
        black_.set({3, 4});
    }

    std::optional<Color> at(const Position& p) const;
    void set(const Position& p, const Color c);
    void clear(const Position& p) {
        white_.clear(p);
        black_.clear(p);
    }
    std::vector<Position> valid_moves(const Color c) const;
    bool place_piece(Color c, const Position& p);

    std::size_t white_count() const {
        return white_.count();
    }

    std::size_t black_count() const {
        return black_.count();
    }

    std::size_t color_count(const Color c) const {
        return pieces(c).count();
    }

    std::vector<Position> white_positions() const {
        return white_.to_position_vector();
    }

    std::vector<Position> black_positions() const {
        return black_.to_position_vector();
    }

    friend std::ostream& operator<<(std::ostream& os, const GameBoard& board);

  private:
    template <Direction D>
    class State;

    BitBoard white_;
    BitBoard black_;

    template <Color C>
    const BitBoard& pieces() const;
    template <Color C>
    const BitBoard& opposite_pieces() const;

    BitBoard& pieces(const Color c) {
        return (c == Color::white) ? white_ : black_;
    }
    const BitBoard& pieces(const Color c) const {
        return (c == Color::white) ? white_ : black_;
    }
    BitBoard& opposite_pieces(const Color c) {
        return pieces(get_opposite_color(c));
    }
    const BitBoard& opposite_pieces(const Color c) const {
        return pieces(get_opposite_color(c));
    }

    BitBoard vacant() const {
        return ~(white_ | black_);
    }

    template <Direction D>
    BitBoard directional_valid_moves(const Color c) const;

    template <Direction D>
    bool directional_capture(const Color c, const Position& p);
    bool capture(const Color c, const Position& p);
};

template <Direction D>
BitBoard GameBoard::directional_valid_moves(const Color c) const {
    BitBoard moves{0};
    BitBoard candidates{opposite_pieces(c) & BitBoard::shift<D>(pieces(c))};
    while (!candidates.empty()) {
        const auto shifted = BitBoard::shift<D>(candidates);
        moves |= vacant() & shifted;
        candidates = opposite_pieces(c) & shifted;
    }
    return moves;
}

template <Direction D>
bool GameBoard::directional_capture(const Color c, const Position& p) {
    State<D> s{c, *this, p};
    bool did_commit = false;
    while (s.should_keep_dilating()) {
        s.dilate();
    }
    if (s.should_commit()) {
        pieces(c) |= s.bits();
        opposite_pieces(c) &= ~s.bits();
        did_commit = true;
    }
    return did_commit;
}

template <Direction D>
class GameBoard::State {
  public:
    State(const Color color, GameBoard& board, const Position& start)
        : my_pieces_(board.pieces(color)), vacant_(board.vacant()), start_{start}, bits_{start} {}

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
void GameBoard::State<D>::dilate() {
    bits_ = bits_.dilate<D>();
}

template <Direction D>
bool GameBoard::State<D>::should_commit() const {
    return capped_;
}

template <Direction D>
bool GameBoard::State<D>::should_keep_dilating() {
    BitBoard selected_ = ~start_ & bits_;
    on_edge_           = bits_.on_edge<D>();
    capped_            = my_pieces_.test_any(selected_);
    on_empty_          = vacant_.test_any(selected_);
    return !(on_edge_ || capped_ || on_empty_);
}

template <Direction D>
const BitBoard& GameBoard::State<D>::bits() const {
    return bits_;
}

} // namespace othello
