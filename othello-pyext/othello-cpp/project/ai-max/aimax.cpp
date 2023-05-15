#include "aimax.h"
#include "board.h"

#include <cassert>

namespace othello {
namespace ai_max {

static int evaluate(const Color C, const GameBoard& board) {
    return (board.pieces_(C).count() - board.opposite_pieces_(C).count());
}

static GameBoard get_next_board(const Color C, const GameBoard& board, const Position& move) {
    GameBoard next_board{board};
    next_board.place_piece(C, move);
    return next_board;
}

// Negamax non-root node evaluation
// Includes only value
static int best_move_inner(const Color C, const GameBoard& board, size_t depth) {
    std::vector<Position> potential_moves = board.valid_moves(C);
    if (potential_moves.empty() || depth == 0) {
        return evaluate(C, board);
    }

    int best_value = std::numeric_limits<int>::min();
    for (auto move : potential_moves) {
        GameBoard next_board{get_next_board(C, board, move)};
        int value = -best_move_inner(C, next_board, depth - 1);
        if (value > best_value) {
            best_value = value;
        }
    }
    return best_value;
}

// Negamax root node evaluation
// Includes both move & value
Position color_best_move(const Color C, const GameBoard& board, size_t depth) {
    std::vector<Position> potential_moves = board.valid_moves(C);
    assert(!potential_moves.empty());

    Position best_move;
    int best_value = std::numeric_limits<int>::min();
    for (auto move : potential_moves) {
        GameBoard next_board{get_next_board(C, board, move)};
        int value = -best_move_inner(C, next_board, depth - 1);
        if (value > best_value) {
            best_value = value;
            best_move  = move;
        }
    }
    return best_move;
}

} // namespace ai_max
} // namespace othello
