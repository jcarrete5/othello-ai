#include "board.h"

#include "gtest/gtest.h"

#include <algorithm>
#include <bitset>

namespace othello {

TEST(Game, Setup) {
    Game game;
    ASSERT_EQ(game.active_color(), Color::black);
    ASSERT_EQ(*game.board().at({3, 3}), Color::white);
    ASSERT_EQ(*game.board().at({4, 4}), Color::white);
    ASSERT_EQ(*game.board().at({3, 4}), Color::black);
    ASSERT_EQ(*game.board().at({4, 3}), Color::black);
}

TEST(Game, ValidMoves) {
    Game game;
    const std::vector<Position> moves = {{3, 2}, {2, 2}, {2, 3}, {2, 4}, {4, 5}, {5, 4}, {1, 2}};
    for (const auto move : moves) {
        const auto valid_moves   = game.valid_moves();
        ASSERT_TRUE(valid_moves.contains(move));

        const auto move_color = game.active_color();
        game.place_piece(move);
        ASSERT_EQ(game.board().at(move), move_color);
    }
}

TEST(Board, InvalidMoves) {
    Game game;
    const std::vector<Position> moves = {{0, 0}, {8, 8}};
    for (const auto move : moves) {
        const auto valid_moves = game.valid_moves();
        ASSERT_FALSE(valid_moves.contains(move));
    }
}

} // namespace othello
