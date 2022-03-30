#include "aimax.h"

#include <limits>
#include <optional>

namespace othello {
namespace AIMax {

int evaluate(const Color color, const GameBoard& board) {
    const GameBoard::Bits& my_pieces  = board.pieces_(color);
    const GameBoard::Bits& opp_pieces = board.opposite_pieces_(color);
    return (bit_board::count(my_pieces) - bit_board::count(opp_pieces));
}

State _best_move_inner(const Color& color, const GameBoard& board, size_t depth) {
    State best;
    best.value = evaluate(color, board);
    best.move = {};
    std::vector<Position> potential_moves = board.valid_moves(color);
    if (depth == 0 || potential_moves.empty())
        return best;

    best.move = *potential_moves.begin();
    best.value = std::numeric_limits<int>::min();
    for (auto move : potential_moves) {
        GameBoard next_board{board};
        next_board.place_piece(color, move);
        State next = _best_move_inner(opposite_color(color), next_board, depth - 1);
        if (next.value > best.value) {
            best.value = next.value;
            best.move  = move;
        }
    }
    return best;
}

Position best_move(const Color& color, const GameBoard& board, size_t depth) {
    State state = _best_move_inner(color, board, depth);
    return *state.move;
}

} // namespace AIMax
} // namespace othello
