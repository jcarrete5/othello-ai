#ifndef OTHELLO_BOARD_H
#define OTHELLO_BOARD_H

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
    if (color == BLACK) return WHITE;
    if (color == WHITE) return BLACK;
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

class BitBoard {
  public:
    using bits_type           = uint64_t;
    static constexpr size_t N = 8;

    BitBoard() : BitBoard(0) {}
    BitBoard(const BitBoard& other) : BitBoard(other.bits) {}
    BitBoard(const uint64_t bits) : bits(bits) {}

    inline static bits_type position_mask(const Position& p) {
        return (TOP_LEFT >> (p.row * 8) >> (p.col));
    }

    inline bool test(const Position& p) const {
        return bits & position_mask(p);
    }

    inline bool count() const {
        return std::bitset<N * N>(bits).count();
    }

    inline void set(const Position& p) {
        bits |= position_mask(p);
    }

    inline void reset(const Position& p) {
        bits &= ~position_mask(p);
    }

    template <Direction>
    bool on_edge() const;

    template <Direction D>
    BitBoard shift(const size_t& n = 1) const;

    template <Direction D>
    BitBoard dilate(const size_t& n = 1) {
        BitBoard dilated{bits};
        for (int i = 0; i < n; i++) {
            dilated |= dilated.shift<D>(n);
        }
        return dilated;
    }

    std::vector<Position> to_positions() const;
    std::bitset<N * N> to_bitset() const;

    std::string to_string() const {
        return std::bitset<N * N>(bits).to_string();
    }

    inline bool operator==(const BitBoard& other) const {
        return bits == other.bits;
    }
    inline bool operator!=(const BitBoard& other) const {
        return bits != other.bits;
    }
    inline BitBoard& operator<<=(size_t n) {
        bits <<= n;
        return *this;
    }
    inline BitBoard operator<<(size_t n) {
        BitBoard result{bits};
        result.bits <<= n;
        return result;
    }
    inline BitBoard& operator>>=(size_t n) {
        bits >>= n;
        return *this;
    }
    inline BitBoard operator>>(size_t n) {
        BitBoard result{bits};
        result.bits >>= n;
        return result;
    }
    inline BitBoard operator|(const BitBoard& other) const {
        BitBoard result{bits};
        result |= other;
        return result;
    }
    inline BitBoard& operator|=(const BitBoard& other) {
        bits |= other.bits;
        return *this;
    }
    inline BitBoard operator&(const BitBoard& other) const {
        BitBoard result{bits};
        result &= other;
        return result;
    }
    inline BitBoard& operator&=(const BitBoard& other) {
        bits &= other.bits;
        return *this;
    }
    inline BitBoard operator^(const BitBoard& other) const {
        return bits ^ other.bits;
    }
    inline BitBoard operator~() const {
        return ~bits;
    }
    operator bool() const {
        return bits;
    }

  private:
    bits_type bits;

    static constexpr const uint64_t TOP_RIGHT =
        0b00000001'00000000'00000000'00000000'00000000'00000000'00000000'00000000;
    static constexpr const uint64_t TOP_LEFT =
        0b10000000'00000000'00000000'00000000'00000000'00000000'00000000'00000000;
    static constexpr const uint64_t BOT_LEFT =
        0b00000000'00000000'00000000'00000000'00000000'00000000'00000000'10000000;
    static constexpr const uint64_t BOT_RIGHT =
        0b00000000'00000000'00000000'00000000'00000000'00000000'00000000'00000001;
    static constexpr const uint64_t TOP_EDGE =
        0b11111111'00000000'00000000'00000000'00000000'00000000'00000000'00000000;
    static constexpr const uint64_t BOT_EDGE =
        0b00000000'00000000'00000000'00000000'00000000'00000000'00000000'11111111;
    static constexpr const uint64_t LEFT_EDGE =
        0b10000000'10000000'10000000'10000000'10000000'10000000'10000000'10000000;
    static constexpr const uint64_t RIGHT_EDGE =
        0b00000001'00000001'00000001'00000001'00000001'00000001'00000001'00000001;
    static constexpr const uint64_t NEG_SLOPE =
        0b10000000'01000000'00100000'00010000'00001000'00000100'00000010'00000001;
    static constexpr const uint64_t POS_SLOPE =
        0b00000001'00000010'00000100'00001000'00010000'00100000'01000000'10000000;
};

class GameBoard {
  public:
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
            black.reset(p);
        } else if (c == BLACK) {
            black.set(p);
            white.reset(p);
        } else if (c == NONE) {
            white.reset(p);
            black.reset(p);
        }
    }

    std::vector<Position> valid_moves(const Color& c) const {
        BitBoard moves = (directional_valid_moves_<RIGHT>(c) | directional_valid_moves_<UPRIGHT>(c) |
                          directional_valid_moves_<UP>(c) | directional_valid_moves_<UPLEFT>(c) |
                          directional_valid_moves_<LEFT>(c) | directional_valid_moves_<DOWNLEFT>(c) |
                          directional_valid_moves_<DOWN>(c) | directional_valid_moves_<DOWNRIGHT>(c));
        return moves.to_positions();
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
BitBoard GameBoard::directional_valid_moves_(const Color& c) const {
    BitBoard moves{0};
    BitBoard candidates{opposite_pieces_(c) & pieces_(c).shift<D>()};
    while (candidates) {
        BitBoard shifted = candidates.shift<D>();
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
        : my_pieces_(board.pieces_(color)), vacant_(board.vacant()), start_(BitBoard::position_mask(start)),
          bits_(BitBoard::position_mask(start)) {}

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
    capped_            = my_pieces_ & selected_;
    on_empty_          = vacant_ & selected_;
    return !(on_edge_ || capped_ || on_empty_);
}

template <Direction D>
const BitBoard& GameBoard::State<D>::bits() const {
    return bits_;
}

} // namespace othello

#endif // OTHELLO_BOARD_H
