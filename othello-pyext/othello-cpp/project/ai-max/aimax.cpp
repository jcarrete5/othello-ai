#include "aimax.h"
#include "board.h"

namespace othello {
namespace AIMax {

template <>
int evaluate_<WHITE>(const GameBoard& board) {
    return (board.t_pieces_<WHITE>().count() - board.t_pieces_<BLACK>().count());
}

template <>
int evaluate_<BLACK>(const GameBoard& board) {
    return (board.t_pieces_<BLACK>().count() - board.t_pieces_<WHITE>().count());
}

Position color_best_move(const Color& color, const GameBoard& board, size_t depth) {
    if (color == WHITE) return best_move_<WHITE>(board, depth);
    if (color == BLACK) return best_move_<BLACK>(board, depth);
    return {0,0};
}

} // namespace AIMax
} // namespace othello
