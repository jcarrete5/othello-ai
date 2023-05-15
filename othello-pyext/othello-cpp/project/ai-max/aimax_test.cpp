#include "aimax.h"
#include "board.h"

#include "gtest/gtest.h"

using namespace othello;

TEST(AIMax, Simple) {
    othello::GameBoard board;
    std::cout << board << std::endl;
    GameBoard::Position move;

    move = othello::ai_max::color_best_move(BLACK, board, 3);
    board.place_piece(BLACK, move);

    move = othello::ai_max::color_best_move(WHITE, board, 3);
    board.place_piece(WHITE, move);

    move = othello::ai_max::color_best_move(BLACK, board, 3);
    board.place_piece(BLACK, move);

    std::cout << board << std::endl;
}
