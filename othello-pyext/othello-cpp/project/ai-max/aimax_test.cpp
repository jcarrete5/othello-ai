#include "aimax.h"
#include "board.h"

#include "gtest/gtest.h"

using namespace othello;

TEST(AIMax, Simple) {
    Game game;
    for (int i = 0; i < 5; ++i) {
        const int depth = 3;
        game.place_piece(othello::ai_max::best_move(game, depth));
    }
}
