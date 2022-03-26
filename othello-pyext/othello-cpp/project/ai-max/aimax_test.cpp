#include "aimax.h"
#include "board.h"

#include "gtest/gtest.h"

using namespace othello;

TEST(AIMax, Dummy) {
    othello::GameBoard board;
    board.place_piece(BLACK, {2,3});
    board.place_piece(WHITE, {2,2});
    std::cout << board << std::endl;
    othello::AIMax::best_move(BLACK, board, 3);
}

