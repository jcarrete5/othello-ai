#include "aimax.h"
#include "board.h"

#include <cassert>

namespace othello {
namespace ai_max {

static int evaluate(const Game& game) {
    const auto& board         = game.board();
    const auto my_color       = game.active_color();
    const auto opponent_color = get_opposite_color(my_color);
    return board.color_count(my_color) - board.color_count(opponent_color);
}

static Game get_next_state(const Game& game, const Position& move) {
    Game next{game};
    next.place_piece(move);
    return next;
}

// Negamax non-root node evaluation
// Includes only value
static int best_move_inner(const Game& game, size_t depth) {
    auto potential_moves = game.valid_moves();
    if (potential_moves.empty() || depth == 0) {
        return evaluate(game);
    }

    auto best_value = std::numeric_limits<int>::min();
    for (auto move : potential_moves) {
        auto value = -best_move_inner(get_next_state(game, move), depth - 1);
        if (value > best_value) {
            best_value = value;
        }
    }
    return best_value;
}

// Negamax root node evaluation
// Includes both move & value
Position best_move(const Game& game, size_t depth) {
    const auto potential_moves = game.valid_moves();
    assert(!potential_moves.empty());

    Position best_move;
    auto best_value = std::numeric_limits<int>::min();
    for (auto move : potential_moves) {
        int value = -best_move_inner(get_next_state(game, move), depth - 1);
        if (value > best_value) {
            best_value = value;
            best_move  = move;
        }
    }
    return best_move;
}

} // namespace ai_max
} // namespace othello
