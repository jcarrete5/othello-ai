#include "aimax.h"
#include "board.h"

#include "gtest/gtest.h"

using namespace othello;

TEST(AIMax, Simple) {
    GameBoard board;
    std::cout << board << std::endl;
    Position move;

    move = othello::ai_max::color_best_move(Color::black, board, 3);
    board.place_piece(Color::black, move);

    move = othello::ai_max::color_best_move(Color::white, board, 3);
    board.place_piece(Color::white, move);

    move = othello::ai_max::color_best_move(Color::black, board, 3);
    board.place_piece(Color::black, move);

    std::cout << board << std::endl;
}
