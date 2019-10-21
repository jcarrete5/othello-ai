import othello.game as game
import othello.bitboard as bb
from othello.player import Color, Player

b = game.Board(game.BoardState(0x0000001008000000, 0x0000000810000000))
print(str(b))
print()
b.place(Color.WHITE, bb.Position(2, 4))
print(str(b))
print()
b.place(Color.BLACK, bb.Position(2, 5))
print(str(b))
print()
b.place(Color.WHITE, bb.Position(4, 2))
print(str(b))
print()
b.place(Color.BLACK, bb.Position(3, 2))
print(str(b))
print()
b.place(Color.WHITE, bb.Position(2, 2))
print(str(b))
