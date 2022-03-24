#pragma once

#include "board.h"

#include <optional>

namespace othello {
namespace AIMax {

struct State {
    Position move;
    int value;
};

int evaluate(const Color color, const GameBoard& board);
std::optional<State> _best_move_inner(const Color& color, const GameBoard& board, size_t depth = 0);
std::optional<Position> best_move(const Color& color, const GameBoard& board);

} // namespace AIMax
} // namespace othello
