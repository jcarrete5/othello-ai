#pragma once

#include "bit_board.h"

#include <array>
#include <bitset>
#include <cstddef>
#include <iostream>
#include <string>
#include <vector>

namespace othello {

enum Color {
    NONE,
    BLACK,
    WHITE,
    MAX_COLOR
};

template <Color C>
struct opposite_color {
    static const Color value;
};

template <>
inline const Color opposite_color<WHITE>::value = BLACK;

template <>
inline const Color opposite_color<BLACK>::value = WHITE;

template <Color C>
inline constexpr Color opposite_color_v = opposite_color<C>::value;

inline Color get_opposite_color(const Color& color) {
    if (color == BLACK)
        return WHITE;
    if (color == WHITE)
        return BLACK;
    return NONE;
}

class GameBoard {
  public:
    using Position = BitBoard::Position;

    GameBoard() {
        set_up();
    }

    void clear() {
        white = BitBoard(0);
        black = BitBoard(0);
    }

    void set_up() {
        clear();
        white.set({3, 3});
        white.set({4, 4});
        black.set({4, 3});
        black.set({3, 4});
    }

    Color at(const Position& p) const {
        bool is_white = white.test(p);
        bool is_black = black.test(p);
        if (!is_white && !is_black)
            return NONE;
        else if (is_white)
            return WHITE;
        else if (is_black)
            return BLACK;
        else
            return MAX_COLOR;
    }

    void set(const Position& p, const Color& c) {
        if (c == WHITE) {
            white.set(p);
            black.clear(p);
        } else if (c == BLACK) {
            black.set(p);
            white.clear(p);
        } else if (c == NONE) {
            white.clear(p);
            black.clear(p);
        }
    }

    std::vector<Position> valid_moves(const Color& c) const {
        BitBoard moves = (directional_valid_moves_<right>(c) | directional_valid_moves_<upright>(c) |
                          directional_valid_moves_<up>(c) | directional_valid_moves_<upleft>(c) |
                          directional_valid_moves_<left>(c) | directional_valid_moves_<downleft>(c) |
                          directional_valid_moves_<down>(c) | directional_valid_moves_<downright>(c));
        return moves.to_position_vector();
    }

    bool place_piece(Color c, const Position& p) {
        bool captured = capture_(c, p);
        if (captured) {
            set(p, c);
        }
        return captured;
    }

    template <Color C>
    const BitBoard& t_pieces_() const;

    template <Color C>
    const BitBoard& t_opposite_pieces_() const;

    BitBoard& pieces_(Color c) {
        return (c == WHITE) ? white : black;
    }
    const BitBoard& pieces_(Color c) const {
        return (c == WHITE) ? white : black;
    }
    BitBoard& opposite_pieces_(Color c) {
        return (c == WHITE) ? black : white;
    }
    const BitBoard& opposite_pieces_(Color c) const {
        return (c == WHITE) ? black : white;
    }

    friend std::ostream& operator<<(std::ostream& os, const GameBoard& board);

  private:
    template <Direction D>
    class State;

    BitBoard white;
    BitBoard black;

    BitBoard vacant() const {
        return ~(white | black);
    }

    template <Direction D>
    BitBoard directional_valid_moves_(const Color& c) const;

    template <Direction D>
    bool directional_capture_(const Color& c, const Position& p);

    bool capture_(const Color& c, const Position& p) {
        bool valid_move = false;
        valid_move |= directional_capture_<right>(c, p);
        valid_move |= directional_capture_<upright>(c, p);
        valid_move |= directional_capture_<up>(c, p);
        valid_move |= directional_capture_<upleft>(c, p);
        valid_move |= directional_capture_<left>(c, p);
        valid_move |= directional_capture_<downleft>(c, p);
        valid_move |= directional_capture_<down>(c, p);
        valid_move |= directional_capture_<downright>(c, p);
        return valid_move;
    }
};

template <Direction D>
BitBoard GameBoard::directional_valid_moves_(const Color& c) const {
    BitBoard moves{0};
    BitBoard candidates{opposite_pieces_(c) & BitBoard::shift<D>(pieces_(c))};
    while (!candidates.empty()) {
        const auto shifted = BitBoard::shift<D>(candidates);
        moves |= vacant() & shifted;
        candidates = opposite_pieces_(c) & shifted;
    }
    return moves;
}

template <Direction D>
bool GameBoard::directional_capture_(const Color& c, const Position& p) {
    State<D> s{c, *this, p};
    bool did_commit = false;
    while (s.should_keep_dilating()) {
        s.dilate();
    }
    if (s.should_commit()) {
        pieces_(c) |= s.bits();
        opposite_pieces_(c) &= ~s.bits();
        did_commit = true;
    }
    return did_commit;
}

template <Direction D>
class GameBoard::State {
  public:
    State(const Color& color, GameBoard& board, const Position& start)
        : my_pieces_(board.pieces_(color)), vacant_(board.vacant()), start_{start}, bits_{start} {}

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
