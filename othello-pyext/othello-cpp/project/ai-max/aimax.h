#pragma once

#include "board.h"

namespace othello {
namespace AIMax {

template <Color C>
GameBoard get_next_board_(const GameBoard& board, const Position& move) {
    GameBoard next_board{board};
    next_board.place_piece(C, move);
    return next_board;
}

template <Color C>
int evaluate_(const GameBoard& board);

// Negamax non-root node evaluation
// Includes only value
template <Color C>
int best_move_inner_(const GameBoard& board, size_t depth) {
    std::vector<Position> potential_moves = board.valid_moves(C);
    if (potential_moves.empty() || depth == 0) {
        return evaluate_<C>(board);
    }

    int best_value = std::numeric_limits<int>::min();
    for (auto move : potential_moves) {
        GameBoard next_board{get_next_board_<C>(board, move)};
        int value = -best_move_inner_<opposite_color_v<C>>(next_board, depth - 1);
        if (value > best_value) {
            best_value = value;
        }
    }
    return best_value;
}

// Negamax root node evaluation
// Includes both move & value
template <Color C>
Position best_move_(const GameBoard& board, size_t depth) {
    std::vector<Position> potential_moves = board.valid_moves(C);
    assert(!potential_moves.empty());
    
    Position best_move;
    int best_value = std::numeric_limits<int>::min();
    for (auto move : potential_moves) {
        GameBoard next_board{get_next_board_<C>(board, move)};
        int value = -best_move_inner_<opposite_color_v<C>>(next_board, depth - 1);
        if (value > best_value) { 
            best_value = value;
            best_move = move;
        }
    }
    return best_move;
}

Position color_best_move(const Color& color, const GameBoard& board, size_t depth);

} // namespace AIMax
} // namespace othello
