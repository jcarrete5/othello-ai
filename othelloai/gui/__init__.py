"""GUI for the othello application."""

import logging
import tkinter as tk
import tkinter.messagebox
from random import choice as choose_from
from typing import Optional

from .player import GUIPlayer
from .. import bitboard as bb
from ..ai import ai_default, ai_options
from ..board import Board
from ..color import Color, opposite_color
from ..game import Game, GameType

_logger = logging.getLogger(__name__)
_game: Optional[Game] = None
_my_player: Optional[GUIPlayer] = None


class BoardView(tk.Canvas):
    """Represents the state of the board graphically."""

    def __init__(self, master):
        self._cell_size = 40
        self._border_width = 0
        self._grid_line_width = 1
        super().__init__(
            master,
            width=self._cell_size * 8 + self._grid_line_width * 7,
            height=self._cell_size * 8 + self._grid_line_width * 7,
            borderwidth=f"{self._border_width}",
            highlightthickness=0,
            bg="#000",
        )
        self.pack()
        self.bind("<Button-1>", self.onclick)

        _logger.debug(
            "Canvas dim (%d, %d)", self.winfo_reqwidth(), self.winfo_reqheight()
        )

        self.redraw(Board(0, 0))

    def onclick(self, event):
        _logger.debug("BoardView clicked %s", event)
        if _my_player is None:
            _logger.debug("My player is None. Ignoring...")
            return

        col = (event.x - self._border_width) / self.winfo_reqwidth() * 8
        row = (event.y - self._border_width) / self.winfo_reqheight() * 8
        _logger.debug("(row=%f, col=%f)", row, col)
        _logger.debug("(row=%d, col=%d)", row, col)
        if 0 <= col < 8 and 0 <= row < 8:
            pos = bb.Position(int(row), int(col))
            _my_player.make_move(pos)

    def redraw(self, board: Board):
        _logger.debug("Redrawing\n%s", board)
        self.delete(tk.ALL)
        for r in range(8):
            for c in range(8):
                x_off = (
                    c * self._cell_size + c * self._grid_line_width + self._border_width
                )
                y_off = (
                    r * self._cell_size + r * self._grid_line_width + self._border_width
                )
                # Draw green empty cell
                self.create_rectangle(
                    x_off,
                    y_off,
                    self._cell_size + x_off,
                    self._cell_size + y_off,
                    fill="#060",
                )

                # Draw piece in cell
                mask = bb.pos_mask(r, c)
                inset = 5
                fill_color = None
                if board.white & mask != 0:
                    fill_color = "#fff"
                elif board.black & mask != 0:
                    fill_color = "#000"
                if fill_color:
                    self.create_oval(
                        x_off + inset,
                        y_off + inset,
                        x_off + self._cell_size - inset,
                        y_off + self._cell_size - inset,
                        fill=fill_color,
                    )


class NewGameDialog(tk.Toplevel):
    """Modal dialog window for creating new games."""

    def __init__(self, parent, board_view: BoardView):
        super().__init__(parent)
        self.transient(parent)
        self.focus_set()
        self.grab_set()
        self.title("New Game")
        self.board_view = board_view

        frame = tk.Frame(self)
        frame.pack_configure(expand=True)

        self.color_var = tk.StringVar(frame, Color.black.name)
        color_frame = tk.LabelFrame(frame, text="Color")
        color_frame.grid(row=0, column=0, sticky="n")
        tk.Radiobutton(
            color_frame, text="Black", variable=self.color_var, value=Color.black.name
        ).grid(row=1, column=1, sticky="w")
        tk.Radiobutton(
            color_frame, text="White", variable=self.color_var, value=Color.white.name
        ).grid(row=2, column=1, sticky="w")
        tk.Radiobutton(
            color_frame, text="Random", variable=self.color_var, value=None
        ).grid(row=3, column=1, sticky="w")

        self.ai_var = tk.StringVar(frame, ai_default)
        ai_frame = tk.LabelFrame(frame, text="AI")
        ai_frame.grid(row=0, column=1, sticky="n")
        for i, ai_name in enumerate(ai_options):
            tk.Radiobutton(
                ai_frame, text=ai_name, variable=self.ai_var, value=ai_name
            ).grid(row=i, column=0, sticky="w")

        self.game_type = tk.StringVar(frame, GameType.computer.name)
        opponent_frame = tk.LabelFrame(frame, text="Opponent")
        opponent_frame.grid(row=0, column=2, sticky="n")
        tk.Radiobutton(
            opponent_frame,
            text="Computer",
            variable=self.game_type,
            value=GameType.computer.name,
        ).grid(row=1, column=0, sticky="w")
        tk.Radiobutton(
            opponent_frame,
            text="Online",
            variable=self.game_type,
            value=GameType.online.name,
            state=tk.DISABLED,
        ).grid(row=2, column=0, sticky="w")

        tk.Button(frame, text="Cancel", command=self.cancel).grid(row=1, column=0)
        tk.Button(frame, text="Start", command=self.submit).grid(row=1, column=1)

        self.bind("<Escape>", lambda e: self.cancel())
        self.bind("<Return>", lambda e: self.submit())
        self.wait_window(self)
        _logger.debug("NewGameDialog closed")

    def cancel(self):
        _logger.debug("Cancel")
        self.destroy()

    def submit(self):
        global _game

        _logger.debug("Submit")

        if _game is not None:
            proceed = tk.messagebox.askokcancel(
                title="Start New Game",
                message="Another game is already in progress. Proceed?",
            )
            if not proceed:
                self.destroy()

        self._reset_game()

        self.destroy()

    def _reset_game(self):
        global _game

        self._make_my_player()
        opponent = self._make_opponent_player(opposite_color(_my_player.color))

        if _game is not None:
            _game.shutdown()

        _game = Game(_my_player, opponent)
        _game.start()

    def _make_my_player(self):
        global _my_player

        my_color = (
            self.color_var.get()
            and Color[self.color_var.get()]
            or choose_from(list(Color))
        )
        _my_player = GUIPlayer(my_color, self.board_view.redraw)

    def _make_opponent_player(self, color: Color):
        game_type = GameType[self.game_type.get()]
        if game_type == GameType.computer:
            OpponentPlayerClass = ai_options[self.ai_var.get()]
            opponent = OpponentPlayerClass(color)
        else:
            assert False, f"{game_type} not implemented"
        return opponent


def _init_widgets(root: tk.Tk):
    root.title("Othello")

    main = tk.Frame(root)
    main.pack_configure(expand=True)
    board_view = BoardView(main)

    menu_bar = tk.Menu(root)
    game_menu = tk.Menu(menu_bar, tearoff=0)
    game_menu.add_command(
        label="New Game...", command=lambda: NewGameDialog(root, board_view)
    )
    menu_bar.add_cascade(label="Game", menu=game_menu)
    root.config(menu=menu_bar)


def loop():
    global _game

    _logger.debug("Init ui loop")

    try:
        root = tk.Tk()
        _init_widgets(root)
        root.mainloop()
    finally:
        if _game is not None:
            _game.shutdown()
