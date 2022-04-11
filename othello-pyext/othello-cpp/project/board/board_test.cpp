#include "board.h"

#include "gtest/gtest.h"

#include <algorithm>
#include <bitset>

namespace othello {

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

TEST(Board, SetAndTest) {
    BitBoard bits;
    for (size_t row = 0; row < 8; row += 1) {
        for (size_t col = (row % 2 == 0) ? 0 : 1; col < 8; col += 2) {
            bits.set({row, col});
        }
    }
    EXPECT_EQ(bits.to_string(), test_board.to_string());
}

TEST(Board, ShiftLeft) {
    BitBoard board{test_board.to_ullong()};
    BitBoard expected{left_board.to_ullong()};

    BitBoard shifted = board.shift<Direction::LEFT>(1);
    EXPECT_EQ(shifted.to_string(), expected.to_string());
}

TEST(Board, ShiftRight) {
    BitBoard board{test_board.to_ullong()};
    BitBoard expected{right_board.to_ullong()};

    BitBoard shifted = board.shift<Direction::RIGHT>(1);
    EXPECT_EQ(shifted.to_string(), expected.to_string());
}

TEST(Board, ShiftUp) {
    BitBoard board{test_board.to_ullong()};
    BitBoard expected{up_board.to_ullong()};

    BitBoard shifted = board.shift<Direction::UP>(1);
    EXPECT_EQ(shifted.to_string(), expected.to_string());
}

TEST(Board, ShiftDown) {
    BitBoard board{test_board.to_ullong()};
    BitBoard expected{down_board.to_ullong()};

    BitBoard shifted = board.shift<Direction::DOWN>(1);
    EXPECT_EQ(shifted.to_string(), expected.to_string());
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

        auto valid_moves   = board.valid_moves(turn_color);
        auto move_in_valid = std::find(valid_moves.begin(), valid_moves.end(), move);
        ASSERT_NE(move_in_valid, valid_moves.end());

        board.place_piece(turn_color, move);
        ASSERT_EQ(board.at(move), turn_color);

        turn_color = get_opposite_color(turn_color);
    }
}

TEST(Board, InvalidMoves) {
    GameBoard board;
    std::vector<Position> moves = {{0, 0}, {8, 8}};
    for (auto move : moves) {
        std::cout << board << std::endl;

        auto valid_moves   = board.valid_moves(BLACK);
        auto move_in_valid = std::find(valid_moves.begin(), valid_moves.end(), move);
        ASSERT_EQ(move_in_valid, valid_moves.end());

        ASSERT_FALSE(board.place_piece(BLACK, move));
    }
}

} // namespace othello
