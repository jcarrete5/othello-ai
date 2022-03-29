#pragma once

#include <array>
#include <bitset>
#include <cstddef>
#include <iostream>
#include <vector>

namespace othello {

enum Color {
    NONE,
    BLACK,
    WHITE,
    MAX_COLOR
};

inline Color opposite_color(const Color& color) {
    if (color == BLACK)
        return WHITE;
    if (color == WHITE)
        return BLACK;
    return NONE;
}

enum Direction {
    MIN_DIRECTION = 0,
    RIGHT         = MIN_DIRECTION,
    UPRIGHT,
    UP,
    UPLEFT,
    LEFT,
    DOWNLEFT,
    DOWN,
    DOWNRIGHT,
    MAX_DIRECTION
};

struct Position {
    size_t row;
    size_t col;

    friend Position operator+(const Position& lhs, const Position& rhs);
    friend Position operator-(const Position& lhs, const Position& rhs);
    friend bool operator==(const Position& lhs, const Position& rhs);
};

namespace bit_board {

inline void display(const uint64_t& bits) {
    std::cout << std::bitset<sizeof(uint64_t) * 8>(bits).to_string() << std::endl;
}

constexpr const uint64_t TOP_RIGHT  = 0b00000001'00000000'00000000'00000000'00000000'00000000'00000000'00000000;
constexpr const uint64_t TOP_LEFT   = 0b10000000'00000000'00000000'00000000'00000000'00000000'00000000'00000000;
constexpr const uint64_t BOT_LEFT   = 0b00000000'00000000'00000000'00000000'00000000'00000000'00000000'10000000;
constexpr const uint64_t BOT_RIGHT  = 0b00000000'00000000'00000000'00000000'00000000'00000000'00000000'00000001;
constexpr const uint64_t TOP_EDGE   = 0b11111111'00000000'00000000'00000000'00000000'00000000'00000000'00000000;
constexpr const uint64_t BOT_EDGE   = 0b00000000'00000000'00000000'00000000'00000000'00000000'00000000'11111111;
constexpr const uint64_t LEFT_EDGE  = 0b10000000'10000000'10000000'10000000'10000000'10000000'10000000'10000000;
constexpr const uint64_t RIGHT_EDGE = 0b00000001'00000001'00000001'00000001'00000001'00000001'00000001'00000001;
constexpr const uint64_t NEG_SLOPE  = 0b10000000'01000000'00100000'00010000'00001000'00000100'00000010'00000001;
constexpr const uint64_t POS_SLOPE  = 0b00000001'00000010'00000100'00001000'00010000'00100000'01000000'10000000;

inline constexpr uint64_t position_mask(const Position& p) {
    return (TOP_LEFT >> (p.row * 8) >> (p.col));
}

inline constexpr bool test(const uint64_t& bits, const Position& p) {
    return bits & position_mask(p);
}

inline constexpr bool count(const uint64_t& bits) {
    return std::bitset<sizeof(uint64_t) * 8>(bits).count();
}

inline void set(uint64_t& bits, const Position& p) {
    bits |= position_mask(p);
}

inline void reset(uint64_t& bits, const Position& p) {
    bits &= ~position_mask(p);
}

template <Direction>
bool on_edge(const uint64_t& bits);

template <Direction D>
uint64_t shift(const uint64_t& bits, const size_t& n = 1);

template <Direction D>
uint64_t dilate(const uint64_t& bits, const size_t& n = 1) {
    uint64_t dilated = bits;
    for (int i = 0; i < n; i++) {
        dilated |= shift<D>(dilated, n);
    }
    return dilated;
}

std::vector<Position> to_positions(const uint64_t& bits);

} // namespace bit_board

class GameBoard {
  public:
    using Bits = uint64_t;

    GameBoard() {
        set_up();
    }

    void clear() {
        white = 0;
        black = 0;
    }

    void set_up() {
        clear();
        bit_board::set(white, {3, 3});
        bit_board::set(white, {4, 4});
        bit_board::set(black, {4, 3});
        bit_board::set(black, {3, 4});
    }

    Color at(const Position& p) const {
        bool is_white = bit_board::test(white, p);
        bool is_black = bit_board::test(black, p);
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
            bit_board::set(white, p);
            bit_board::reset(black, p);
        } else if (c == BLACK) {
            bit_board::set(black, p);
            bit_board::reset(white, p);
        } else if (c == NONE) {
            bit_board::reset(white, p);
            bit_board::reset(black, p);
        }
    }

    Bits vacant() const {
        return ~(white | black);
    }

    std::vector<Position> valid_moves(const Color& c) const {
        Bits moves = (directional_valid_moves_<RIGHT>(c) | directional_valid_moves_<UPRIGHT>(c) |
                      directional_valid_moves_<UP>(c) | directional_valid_moves_<UPLEFT>(c) |
                      directional_valid_moves_<LEFT>(c) | directional_valid_moves_<DOWNLEFT>(c) |
                      directional_valid_moves_<DOWN>(c) | directional_valid_moves_<DOWNRIGHT>(c));
        return bit_board::to_positions(moves);
    }

    bool place_piece(Color c, const Position& p) {
        bool captured = capture_(c, p);
        if (captured) {
            set(p, c);
        }
        return captured;
    }

    Bits& pieces_(Color c) {
        return (c == WHITE) ? white : black;
    }
    const Bits& pieces_(Color c) const {
        return (c == WHITE) ? white : black;
    }
    Bits& opposite_pieces_(Color c) {
        return (c == WHITE) ? black : white;
    }
    const Bits& opposite_pieces_(Color c) const {
        return (c == WHITE) ? black : white;
    }

    friend std::ostream& operator<<(std::ostream& os, const GameBoard& board);

  private:
    template <Direction D>
    class State;

    Bits white;
    Bits black;

    template <Direction D>
    Bits directional_valid_moves_(const Color& c) const;

    template <Direction D>
    bool directional_capture_(const Color& c, const Position& p);

    bool capture_(const Color& c, const Position& p) {
        bool valid_move = false;
        valid_move |= directional_capture_<RIGHT>(c, p);
        valid_move |= directional_capture_<UPRIGHT>(c, p);
        valid_move |= directional_capture_<UP>(c, p);
        valid_move |= directional_capture_<UPLEFT>(c, p);
        valid_move |= directional_capture_<LEFT>(c, p);
        valid_move |= directional_capture_<DOWNLEFT>(c, p);
        valid_move |= directional_capture_<DOWN>(c, p);
        valid_move |= directional_capture_<DOWNRIGHT>(c, p);
        return valid_move;
    }
};

template <Direction D>
GameBoard::Bits GameBoard::directional_valid_moves_(const Color& c) const {
    Bits moves      = 0;
    Bits candidates = opposite_pieces_(c) & bit_board::shift<D>(pieces_(c));
    while (candidates) {
        Bits shifted = bit_board::shift<D>(candidates);
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
        : my_pieces_(board.pieces_(color)), vacant_(board.vacant()), start_(bit_board::position_mask(start)),
          bits_(bit_board::position_mask(start)) {}

    void dilate();
    bool should_commit() const;
    bool should_keep_dilating();
    const Bits& bits() const;

  private:
    Bits start_;
    Bits my_pieces_;
    Bits vacant_;

    Bits bits_;
    bool capped_;
    bool on_edge_;
    bool on_empty_;
};

template <Direction D>
void GameBoard::State<D>::dilate() {
    bits_ = bit_board::dilate<D>(bits_);
}

template <Direction D>
bool GameBoard::State<D>::should_commit() const {
    return capped_;
}

template <Direction D>
bool GameBoard::State<D>::should_keep_dilating() {
    Bits selected_ = ~start_ & bits_;
    on_edge_       = bit_board::on_edge<D>(bits_);
    capped_        = my_pieces_ & selected_;
    on_empty_      = vacant_ & selected_;
    return !(on_edge_ || capped_ || on_empty_);
}

template <Direction D>
const GameBoard::Bits& GameBoard::State<D>::bits() const {
    return bits_;
}

} // namespace othello
