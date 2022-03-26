#include "board.h"

#include "gtest/gtest.h"

#include <bitset>

namespace othello {
namespace bb = bit_board;

static const std::bitset<64> test_board{"10101010"
                                        "01010101"
                                        "10101010"
                                        "01010101"
                                        "10101010"
                                        "01010101"
                                        "10101010"
                                        "01010101"};

static const std::bitset<64> down_board{"00000000"
                                        "10101010"
                                        "01010101"
                                        "10101010"
                                        "01010101"
                                        "10101010"
                                        "01010101"
                                        "10101010"};

static const std::bitset<64> up_board{"01010101"
                                      "10101010"
                                      "01010101"
                                      "10101010"
                                      "01010101"
                                      "10101010"
                                      "01010101"
                                      "00000000"};

static const std::bitset<64> left_board{"01010100"
                                        "10101010"
                                        "01010100"
                                        "10101010"
                                        "01010100"
                                        "10101010"
                                        "01010100"
                                        "10101010"};

static const std::bitset<64> right_board{"01010101"
                                         "00101010"
                                         "01010101"
                                         "00101010"
                                         "01010101"
                                         "00101010"
                                         "01010101"
                                         "00101010"};

TEST(Board, Constants) {
    EXPECT_EQ(std::bitset<64>(bb::position_mask({0, 0})).to_string(), std::bitset<64>(bb::TOP_LEFT).to_string());
}

TEST(Board, SetAndTest) {
    uint64_t bits = 0;
    for (size_t row = 0; row < 8; row += 1) {
        for (size_t col = (row % 2 == 0) ? 0 : 1; col < 8; col += 2) {
            bb::set(bits, {row, col});
        }
    }
    EXPECT_EQ(std::bitset<64>(bits).to_string(), test_board.to_string());
}

TEST(Board, ShiftLeft) {
    std::bitset<64> board_bits    = test_board;
    std::bitset<64> expected_bits = left_board;

    uint64_t shifted = bb::shift<Direction::LEFT>(board_bits.to_ullong(), 1);
    EXPECT_EQ(std::bitset<64>(shifted).to_string(), expected_bits.to_string());
}

TEST(Board, ShiftRight) {
    std::bitset<64> board_bits    = test_board;
    std::bitset<64> expected_bits = right_board;

    uint64_t shifted = bb::shift<Direction::RIGHT>(board_bits.to_ullong(), 1);
    EXPECT_EQ(std::bitset<64>(shifted).to_string(), expected_bits.to_string());
}

TEST(Board, ShiftUp) {
    std::bitset<64> board_bits    = test_board;
    std::bitset<64> expected_bits = up_board;

    uint64_t shifted = bb::shift<Direction::UP>(board_bits.to_ullong(), 1);
    EXPECT_EQ(std::bitset<64>(shifted).to_string(), expected_bits.to_string());
}

TEST(Board, ShiftDown) {
    std::bitset<64> board_bits    = test_board;
    std::bitset<64> expected_bits = down_board;

    uint64_t shifted = bb::shift<Direction::DOWN>(board_bits.to_ullong(), 1);
    EXPECT_EQ(std::bitset<64>(shifted).to_string(), expected_bits.to_string());
}

TEST(Board, Setup) {
    GameBoard board;
    ASSERT_EQ(board.at({3, 3}), WHITE);
    ASSERT_EQ(board.at({4, 4}), WHITE);
    ASSERT_EQ(board.at({3, 4}), BLACK);
    ASSERT_EQ(board.at({4, 3}), BLACK);
}

TEST(Board, ValidMoves) {
    GameBoard board;
    std::vector<Position> moves = {{3, 2}, {2, 2}, {2, 3}, {2, 4}, {4, 5}, {5, 4}, {1, 2}};
    Color turn_color            = BLACK;
    for (auto move : moves) {
        std::cout << board << std::endl;
        board.place_piece(turn_color, move);
        ASSERT_EQ(board.at(move), turn_color);
        turn_color = opposite_color(turn_color);
    }
}

TEST(Board, InvalidMoves) {
    GameBoard board;
    std::vector<Position> moves = {{3, 3}, {0, 0}};
    for (auto move : moves) {
        std::cout << board << std::endl;
        ASSERT_FALSE(board.place_piece(BLACK, move));
    }
}

} // namespace othello
