#include "board.h"

#include "gtest/gtest.h"

#include <algorithm>
#include <bitset>

namespace othello {

TEST(Board, Setup) {
    GameBoard board;
    ASSERT_EQ(*board.at({3, 3}), Color::white);
    ASSERT_EQ(*board.at({4, 4}), Color::white);
    ASSERT_EQ(*board.at({3, 4}), Color::black);
    ASSERT_EQ(*board.at({4, 3}), Color::black);
}

TEST(Board, ValidMoves) {
    GameBoard board;
    std::vector<GameBoard::Position> moves = {{3, 2}, {2, 2}, {2, 3}, {2, 4}, {4, 5}, {5, 4}, {1, 2}};
    Color turn_color                       = Color::black;
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
    std::vector<GameBoard::Position> moves = {{0, 0}, {8, 8}};
    for (auto move : moves) {
        std::cout << board << std::endl;

        auto valid_moves   = board.valid_moves(Color::black);
        auto move_in_valid = std::find(valid_moves.begin(), valid_moves.end(), move);
        ASSERT_EQ(move_in_valid, valid_moves.end());
    }
}

} // namespace othello
