#include "aimax.h"
#include "board.h"

#include "gtest/gtest.h"

using namespace othello;

TEST(AIMax, Dummy) {
    othello::GameBoard board;
    std::cout << board << std::endl;
    Position move;

    move = othello::AIMax::best_move(BLACK, board, 3);
    board.place_piece(BLACK, move);

    move = othello::AIMax::best_move(WHITE, board, 3);
    board.place_piece(WHITE, move);

    move = othello::AIMax::best_move(BLACK, board, 3);
    board.place_piece(BLACK, move);

    std::cout << board << std::endl;
}
