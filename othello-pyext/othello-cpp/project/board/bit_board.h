#pragma once

#include "vec2.h"

#include <cassert>

#include <exception>
#include <set>
#include <vector>

enum class Direction
{
    right,
    upright,
    up,
    upleft,
    left,
    downleft,
    down,
    downright,
};

class BitBoard
{
  public:
    using Position = dm::Vec2<int>;
    using Bits = std::uint64_t;

    static constexpr int board_size = 8;
    static constexpr std::size_t n_bits = 64;
    static_assert(sizeof(Bits) * CHAR_BIT == n_bits, "number of bits mismatch");

    constexpr explicit BitBoard() : BitBoard(0) {}
    constexpr explicit BitBoard(const Bits bits) : bits_(bits) {}
    constexpr explicit BitBoard(const Position& position) : BitBoard(from_position(position)) {}
    explicit BitBoard(const std::string& board);

    constexpr BitBoard(const BitBoard& other) = default;
    constexpr BitBoard& operator=(const BitBoard&) = default;

    constexpr BitBoard(BitBoard&& other) = default;
    constexpr BitBoard& operator=(BitBoard&&) = default;

    static BitBoard make_top_right()
    {
        return BitBoard{top_right};
    }

    static constexpr BitBoard make_top_left()
    {
        return BitBoard{top_left};
    }

    static constexpr BitBoard make_bottom_left()
    {
        return BitBoard{bottom_left};
    }

    static constexpr BitBoard make_bottom_right()
    {
        return BitBoard{bottom_right};
    }

    static constexpr BitBoard make_right_edge()
    {
        return BitBoard{right_edge};
    }

    static constexpr BitBoard make_top_right_edge()
    {
        return BitBoard{top_right_edge};
    }

    static constexpr BitBoard make_top_edge()
    {
        return BitBoard{top_edge};
    }

    static constexpr BitBoard make_top_left_edge()
    {
        return BitBoard{top_left_edge};
    }

    static constexpr BitBoard make_left_edge()
    {
        return BitBoard{left_edge};
    }

    static constexpr BitBoard make_bottom_left_edge()
    {
        return BitBoard{bottom_left_edge};
    }

    static constexpr BitBoard make_bottom_edge()
    {
        return BitBoard{bottom_edge};
    }

    static constexpr BitBoard make_bottom_right_edge()
    {
        return BitBoard{bottom_right_edge};
    }

    static constexpr BitBoard make_all_edge()
    {
        return BitBoard{all_edge};
    }

    static constexpr BitBoard make_positive_slope()
    {
        return BitBoard{positive_slope};
    }

    static constexpr BitBoard make_negative_slope()
    {
        return BitBoard{negative_slope};
    }

    static constexpr BitBoard make_full()
    {
        return ~BitBoard{};
    }

    template <Direction D>
    [[nodiscard]] static BitBoard shift(BitBoard board, size_t n = 1)
    {
        return board.shift_assign<D>(n);
    }

    [[nodiscard]] static BitBoard shift(BitBoard board, Direction direction, size_t n = 1);

    static BitBoard neighbors_cardinal(const Position& position);
    static BitBoard neighbors_diagonal(const Position& position);
    static BitBoard neighbors_cardinal_and_diagonal(const Position& position);

    [[nodiscard]] bool test(const Position& position) const
    {
        return test_any(BitBoard{position});
    }

    [[nodiscard]] bool test_any(const BitBoard other) const
    {
        return !(*this & other).empty();
    }

    [[nodiscard]] bool test_all(const BitBoard other) const
    {
        return (*this & other) == other;
    }

    [[nodiscard]] bool empty() const
    {
        return bits_ == 0U;
    }

    [[nodiscard]] std::size_t count() const;

    BitBoard& set(const BitBoard other)
    {
        bits_ |= other.bits_;
        return *this;
    }

    BitBoard& set(const Position& position)
    {
        return set(BitBoard{position});
    }

    BitBoard& clear(const BitBoard other)
    {
        *this &= ~other;
        return *this;
    }

    BitBoard& clear(const Position& position)
    {
        return clear(BitBoard{position});
    }

    BitBoard& clear_all()
    {
        bits_ = 0U;
        return *this;
    }

    template <Direction D>
    [[nodiscard]] bool on_edge() const;

    [[nodiscard]] bool on_edge(Direction direction) const;

    [[nodiscard]] bool on_any_edge() const;

    template <Direction D>
    BitBoard& shift_assign(size_t n = 1);

    BitBoard& shift_assign(Direction direction, size_t n = 1);

    BitBoard& shift_assign(Position relative_offset);

    template <Direction D>
    BitBoard& dilate()
    {
        return *this |= BitBoard::shift<D>(*this);
    }

    template <Direction D>
    BitBoard& dilate(const size_t n)
    {
        for (size_t i = 0; i < n; i++) {
            dilate<D>();
        }
        return *this;
    }

    BitBoard& dilate(Direction direction, size_t n = 1);

    [[nodiscard]] std::vector<Position> to_position_vector() const;
    [[nodiscard]] std::vector<BitBoard> to_bitboard_position_vector() const;
    [[nodiscard]] Position to_position() const;
    [[nodiscard]] std::set<Position> to_position_set() const;
    [[nodiscard]] unsigned long long to_ullong() const
    {
        return bits_;
    }

    [[nodiscard]] std::string to_string() const;

    bool operator==(const BitBoard other) const
    {
        return bits_ == other.bits_;
    }
    bool operator!=(const BitBoard other) const
    {
        return !(*this == other);
    }
    BitBoard& operator<<=(size_t n)
    {
        bits_ <<= n;
        return *this;
    }
    BitBoard operator<<(size_t n) const
    {
        return BitBoard{*this} <<= n;
    }
    BitBoard& operator>>=(size_t n)
    {
        bits_ >>= n;
        return *this;
    }
    BitBoard operator>>(size_t n) const
    {
        return BitBoard{*this} >>= n;
    }
    BitBoard& operator|=(const BitBoard other)
    {
        bits_ |= other.bits_;
        return *this;
    }
    BitBoard operator|(const BitBoard other) const
    {
        return BitBoard{*this} |= other;
    }
    BitBoard& operator&=(const BitBoard other)
    {
        bits_ &= other.bits_;
        return *this;
    }
    BitBoard operator&(const BitBoard other) const
    {
        return BitBoard{*this} &= other;
    }
    BitBoard& operator^=(const BitBoard other)
    {
        bits_ ^= other.bits_;
        return *this;
    }
    BitBoard operator^(const BitBoard other) const
    {
        return BitBoard{bits_ ^ other.bits_};
    }
    BitBoard operator~() const
    {
        return BitBoard{~bits_};
    }

  private:
    Bits bits_;

    static constexpr Bits top_right = 0b00000001'00000000'00000000'00000000'00000000'00000000'00000000'00000000;
    static constexpr Bits top_left = 0b10000000'00000000'00000000'00000000'00000000'00000000'00000000'00000000;
    static constexpr Bits bottom_left = 0b00000000'00000000'00000000'00000000'00000000'00000000'00000000'10000000;
    static constexpr Bits bottom_right = 0b00000000'00000000'00000000'00000000'00000000'00000000'00000000'00000001;
    static constexpr Bits top_edge = 0b11111111'00000000'00000000'00000000'00000000'00000000'00000000'00000000;
    static constexpr Bits bottom_edge = 0b00000000'00000000'00000000'00000000'00000000'00000000'00000000'11111111;
    static constexpr Bits left_edge = 0b10000000'10000000'10000000'10000000'10000000'10000000'10000000'10000000;
    static constexpr Bits right_edge = 0b00000001'00000001'00000001'00000001'00000001'00000001'00000001'00000001;
    static constexpr Bits top_right_edge = top_edge | right_edge;
    static constexpr Bits top_left_edge = top_edge | left_edge;
    static constexpr Bits bottom_right_edge = bottom_edge | right_edge;
    static constexpr Bits bottom_left_edge = bottom_edge | left_edge;
    static constexpr Bits all_edge = right_edge | top_edge | left_edge | bottom_edge;
    static constexpr Bits negative_slope = 0b10000000'01000000'00100000'00010000'00001000'00000100'00000010'00000001;
    static constexpr Bits positive_slope = 0b00000001'00000010'00000100'00001000'00010000'00100000'01000000'10000000;

    inline static constexpr BitBoard from_position(const Position& position);
    inline static constexpr Position index_to_position(std::size_t index);

    friend void swap(BitBoard& lhs, BitBoard& rhs)
    {
        std::swap(lhs.bits_, rhs.bits_);
    }
};

constexpr BitBoard BitBoard::from_position(const Position& position)
{
    if (position.x() < 0 || position.x() >= board_size || position.y() < 0 || position.y() >= board_size) {
        throw std::invalid_argument("position outside of board");
    }
    auto board = BitBoard::make_top_left();
    board.bits_ >>= position.x() * board_size;
    board.bits_ >>= position.y();
    return board;
}

constexpr BitBoard::Position BitBoard::index_to_position(const std::size_t index)
{
    using T = Position::dimension_type;
    return {static_cast<T>(index / board_size), static_cast<T>(index % board_size)};
}
