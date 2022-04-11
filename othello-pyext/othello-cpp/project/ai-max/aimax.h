#pragma once

#include "board.h"

namespace othello {
namespace AIMax {

// Negamax root node evaluation
// Includes both move & value
Position color_best_move(const Color C, const GameBoard& board, size_t depth);

} // namespace AIMax
} // namespace othello
