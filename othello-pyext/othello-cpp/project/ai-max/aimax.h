#pragma once

#include "board.h"

namespace othello {
namespace ai_max {

// Negamax root node evaluation
// Includes both move & value
Position color_best_move(const Color C, const GameBoard& board, size_t depth);

} // namespace ai_max
} // namespace othello
