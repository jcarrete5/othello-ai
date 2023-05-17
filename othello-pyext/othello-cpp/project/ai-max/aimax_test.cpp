#include "aimax.h"
#include "board.h"

#include "gtest/gtest.h"

using namespace othello;

TEST(AIMax, Simple) {
    const int n_games = 10;
    const int depth   = 8;
    Game game;
    for (int i = 0; i < n_games; ++i) {
        while (!game.is_game_over()) {
            if (game.has_valid_move()) {
                game.place_piece(othello::ai_max::best_move(game, depth));
            }
            game.next_turn();
        }
    }
}
