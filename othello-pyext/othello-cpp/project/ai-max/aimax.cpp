#include "aimax.h"
#include "board.h"

#include <cassert>

namespace othello {
namespace ai_max {

static int evaluate(const Color c, const GameBoard& board) {
    return board.color_count(c) - board.color_count(get_opposite_color(c));
}

static GameBoard get_next_board(const Color c, const GameBoard& board, const Position& move) {
    GameBoard next_board{board};
    next_board.place_piece(c, move);
    return next_board;
}

// Negamax non-root node evaluation
// Includes only value
static int best_move_inner(const Color c, const GameBoard& board, size_t depth) {
    std::vector<Position> potential_moves = board.valid_moves(c);
    if (potential_moves.empty() || depth == 0) {
        return evaluate(c, board);
    }

    int best_value = std::numeric_limits<int>::min();
    for (auto move : potential_moves) {
        GameBoard next_board{get_next_board(c, board, move)};
        int value = -best_move_inner(c, next_board, depth - 1);
        if (value > best_value) {
            best_value = value;
        }
    }
    return best_value;
}

// Negamax root node evaluation
// Includes both move & value
Position color_best_move(const Color c, const GameBoard& board, size_t depth) {
    std::vector<Position> potential_moves = board.valid_moves(c);
    assert(!potential_moves.empty());

    Position best_move;
    int best_value = std::numeric_limits<int>::min();
    for (auto move : potential_moves) {
        GameBoard next_board{get_next_board(c, board, move)};
        int value = -best_move_inner(c, next_board, depth - 1);
        if (value > best_value) {
            best_value = value;
            best_move  = move;
        }
    }
    return best_move;
}

} // namespace ai_max
} // namespace othello
