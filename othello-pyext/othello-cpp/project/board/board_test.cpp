#include "board.h"

#include "gtest/gtest.h"

#include <bitset>

namespace othello {
namespace bb = bit_board;

static const std::bitset<64> test_board{"10000000"
                                        "01000000"
                                        "00100000"
                                        "00010000"
                                        "00001000"
                                        "00000100"
                                        "00000010"
                                        "00000001"};

static const std::bitset<64> down_left_board{"00000000"
                                             "00000000"
                                             "10000000"
                                             "01000000"
                                             "00100000"
                                             "00010000"
                                             "00001000"
                                             "00000100"};

static const std::bitset<64> up_right_board{"00100000"
                                            "00010000"
                                            "00001000"
                                            "00000100"
                                            "00000010"
                                            "00000001"
                                            "00000000"
                                            "00000000"};

TEST(Board, Constants) {
    EXPECT_EQ(std::bitset<64>(bb::position_mask({0, 0})).to_string(), std::bitset<64>(bb::TOP_LEFT).to_string());
    EXPECT_EQ(test_board.to_string(), std::bitset<64>(bb::NEG_SLOPE).to_string());
}

TEST(Board, SetAndTest) {
    uint64_t bits = 0;
    Position p;
    for (int i = 0; i < 8; i++) {
        p.row = i;
        p.col = i;
        bb::set(bits, p);
    }
    EXPECT_EQ(std::bitset<64>(bits).to_string(), test_board.to_string());
}

TEST(Board, ShiftLeft) {
    std::bitset<64> board_bits    = test_board;
    std::bitset<64> expected_bits = down_left_board;

    uint64_t shifted = bb::shift<Direction::LEFT>(board_bits.to_ullong(), 2);
    EXPECT_EQ(std::bitset<64>(shifted).to_string(), expected_bits.to_string());
}

TEST(Board, ShiftRight) {
    std::bitset<64> board_bits    = test_board;
    std::bitset<64> expected_bits = up_right_board;

    uint64_t shifted = bb::shift<Direction::RIGHT>(board_bits.to_ullong(), 2);
    EXPECT_EQ(std::bitset<64>(shifted).to_string(), expected_bits.to_string());
}

TEST(Board, ShiftUp) {
    std::bitset<64> board_bits    = test_board;
    std::bitset<64> expected_bits = up_right_board;

    uint64_t shifted = bb::shift<Direction::UP>(board_bits.to_ullong(), 2);
    EXPECT_EQ(std::bitset<64>(shifted).to_string(), expected_bits.to_string());
}

TEST(Board, ShiftDown) {
    std::bitset<64> board_bits    = test_board;
    std::bitset<64> expected_bits = down_left_board;

    uint64_t shifted = bb::shift<Direction::DOWN>(board_bits.to_ullong(), 2);
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
    Position p;

    p = Position{3, 2};
    board.place_piece(BLACK, p);
    std::cout << board << std::endl;
    ASSERT_EQ(board.at(p), BLACK);


    p = Position{2, 2};
    board.place_piece(WHITE, p);
    std::cout << board << std::endl;
    ASSERT_EQ(board.at(p), WHITE);

    p = Position{2, 3};
    board.place_piece(BLACK, p);
    std::cout << board << std::endl;
    ASSERT_EQ(board.at(p), BLACK);

    p = Position{2, 4};
    board.place_piece(WHITE, p);
    std::cout << board << std::endl;
    ASSERT_EQ(board.at(p), WHITE);

    p = Position{4, 5};
    board.place_piece(BLACK, p);
    std::cout << board << std::endl;
    ASSERT_EQ(board.at(p), BLACK);

    p = Position{5, 4};
    board.place_piece(WHITE, p);
    std::cout << board << std::endl;
    ASSERT_EQ(board.at(p), WHITE);

    p = Position{1, 2};
    board.place_piece(BLACK, p);
    std::cout << board << std::endl;
    ASSERT_EQ(board.at(p), BLACK);
}

} // namespace othello
