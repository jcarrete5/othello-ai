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

std::optional<State> _best_move_inner(const Color& color, const GameBoard& board, size_t depth) {
    if (depth == 0)
        return {};

    std::vector<Position> potential_moves = board.valid_moves(color);
    if (potential_moves.empty())
        return {};

    State current;
    current.value = std::numeric_limits<int>::min();
    for (auto move : potential_moves) {
        GameBoard next_board{board};
        next_board.place_piece(color, move);
        auto next = _best_move_inner(opposite_color(color), next_board, depth - 1);
        if (!next) {
            current.value = evaluate(color, next_board);
        } else {
            next->value *= -1;
            if (next->value > current.value) {
                current.value = next->value;
                current.move  = move;
            }
        }
    }
    return current;
}

Position best_move(const Color& color, const GameBoard& board, size_t depth) {
    //std::cout << "called best_move(color={" << color << "}, board={" << board << "}, depth={" << depth << "})" << std::endl;
    auto state = _best_move_inner(color, board, depth);
    return state->move;
}

} // namespace AIMax
} // namespace othello
