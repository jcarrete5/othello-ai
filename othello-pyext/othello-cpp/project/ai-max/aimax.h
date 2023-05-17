#pragma once

#include "board.h"

namespace othello {
namespace ai_max {

// Negamax root node evaluation
// Includes both move & value
Position best_move(const Game& game, size_t depth);

} // namespace ai_max
} // namespace othello
