#include "aimax.h"
#include "board.h"

#include <cassert>

#include <array>

namespace othello::ai_max {

const static auto min_score = std::numeric_limits<int>::min();
const static auto max_score = std::numeric_limits<int>::max();

static int evaluate(const Game& game)
{
    static constexpr auto corner_extra_weight = 5;
    const auto& board = game.board();
    const auto my_color = game.active_color();
    const auto opponent_color = get_opposite_color(my_color);
    const auto my_pieces = board.pieces(my_color);
    const auto opponent_pieces = board.pieces(opponent_color);
    const auto n_mine = static_cast<int>(my_pieces.count());
    const auto n_opponent = static_cast<int>(opponent_pieces.count());

    if (game.is_game_over()) {
        return n_mine - n_opponent;
    }

    const auto n_corners_mine = static_cast<int>((my_pieces & BitBoard::make_all_corners()).count());
    const auto n_corners_opponent = static_cast<int>((opponent_pieces & BitBoard::make_all_corners()).count());

    return n_mine - n_opponent + corner_extra_weight * (n_corners_mine - n_corners_opponent);
}

static Game get_next_state(const Game& game, const BitBoard move)
{
    Game next{game};
    next.place_piece_bitboard_position(move);
    return next;
}

// Negamax non-root node evaluation
// Includes only value
static int best_move_inner(const Game& game, size_t depth)
{
    auto potential_moves = game.valid_moves_bitboard();
    if (potential_moves.empty() || depth == 0) {
        return evaluate(game);
    }

    auto best_value = min_score;
    for (auto move : potential_moves.to_bitboard_position_vector()) {
        const auto value = -best_move_inner(get_next_state(game, move), depth - 1);
        if (value > best_value) {
            best_value = value;
        }
    }
    return best_value;
}

// Negamax non-root node evaluation
// Includes only value
// Alpha-Beta pruning optimization
static int best_move_inner_a_b(const Game& game, int alpha, int beta, size_t depth)
{
    auto potential_moves = game.valid_moves_bitboard();
    if (potential_moves.empty() || depth == 0) {
        return evaluate(game);
    }

    auto best_value = std::numeric_limits<int>::min();
    for (auto move : potential_moves.to_bitboard_position_vector()) {
        const auto value = -best_move_inner_a_b(get_next_state(game, move), -beta, -alpha, depth - 1);
        if (value > best_value) {
            best_value = value;
        }
        alpha = std::max(alpha, value);
        if (alpha > beta) {
            break;
        }
    }
    return best_value;
}

// Negamax root node evaluation
// Includes both move & value
Position best_move(const Game& game, size_t depth)
{
    const auto potential_moves = game.valid_moves_bitboard();
    assert(!potential_moves.empty());

    Position best_move;
    auto best_value = min_score;
    int alpha = min_score;
    int beta = max_score;
    for (auto move : potential_moves.to_bitboard_position_vector()) {
        const int value = -best_move_inner_a_b(get_next_state(game, move), -beta, -alpha, depth - 1);
        if (value > best_value) {
            best_value = value;
            best_move = move.to_position();
        }
        alpha = std::max(alpha, value);
        if (alpha > beta) {
            break;
        }
    }
    return best_move;
}

} // namespace othello::ai_max
