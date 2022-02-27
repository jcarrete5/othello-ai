"""GUI for the othello application."""

import logging
import tkinter as tk
import tkinter.messagebox
from random import choice as choose_from
from typing import Optional

from .player import GUIPlayer
from .. import bitboard as bb
from ..ai import ai_default, ai_options, AIOption
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
        self.board_view = board_view
        self.ai_settings = dict(depth=3)

        # Frames
        self.frame = tk.Frame(self)
        self.frame_color = tk.LabelFrame(self.frame, text="Color")
        self.frame_ai = tk.LabelFrame(self.frame, text="AI")
        self.frame_gametype = tk.LabelFrame(self.frame, text="Opponent")
        self.frame_ai_settings = tk.LabelFrame(self.frame_ai, text="Settings", border=0)

        # Variables
        self.color_var = tk.StringVar(self.frame, Color.black.name)
        self.game_type_var = tk.StringVar(self.frame, GameType.computer.name)
        self.ai_var = tk.StringVar(self.frame, ai_default.name)
        self.depth_var = tk.IntVar(self.frame, self.ai_settings["depth"])

        # Radio buttons
        self.radiobutton_color_black = tk.Radiobutton(
            self.frame_color,
            text="Black",
            variable=self.color_var,
            value=Color.black.name,
        )
        self.radiobutton_color_white = tk.Radiobutton(
            self.frame_color,
            text="White",
            variable=self.color_var,
            value=Color.white.name,
        )
        self.radiobutton_color_random = tk.Radiobutton(
            self.frame_color, text="Random", variable=self.color_var, value=None
        )
        self.radiobutton_gametype_computer = tk.Radiobutton(
            self.frame_gametype,
            text="Computer",
            variable=self.game_type_var,
            value=GameType.computer.name,
        )
        self.radiobutton_gametype_online = tk.Radiobutton(
            self.frame_gametype,
            text="Online",
            variable=self.game_type_var,
            value=GameType.online.name,
            state=tk.DISABLED,
        )

        # Buttons
        self.button_cancel = tk.Button(self.frame, text="Cancel", command=self.cancel)
        self.button_start = tk.Button(self.frame, text="Start", command=self.submit)

        # Option menus
        self.optionmenu_ai = tk.OptionMenu(
            self.frame_ai, self.ai_var, *(ai.name for ai in ai_options)
        )

        # Spinbox
        self.spinbox_minmax_depth = tk.Spinbox(
            self.frame_ai_settings,
            textvariable=self.depth_var,
            width=5,
            from_=1,
            to=10,
            increment=1,
        )

        # Labels
        self.label_depth = tk.Label(self.frame_ai_settings, text="Depth:")

        # Configure
        self.transient(parent)
        self.focus_set()
        self.grab_set()
        self.title("New Game")
        self.frame.pack_configure(expand=True)

        # Bindings
        self.bind("<Escape>", lambda e: self.cancel())
        self.bind("<Return>", lambda e: self.submit())
        self.ai_var.trace_add(
            "write", callback=lambda *args: self._layout_ai_settings()
        )
        self.depth_var.trace_add(
            "write",
            callback=lambda *args: self.ai_settings.update(depth=self.depth_var.get()),
        )

        self._layout()

        self.wait_window(self)
        _logger.debug("NewGameDialog closed")

    def _layout(self):
        self.frame_color.grid(row=0, column=0, sticky="n")
        self.radiobutton_color_black.grid(row=1, column=1, sticky="w")
        self.radiobutton_color_white.grid(row=2, column=1, sticky="w")
        self.radiobutton_color_random.grid(row=3, column=1, sticky="w")

        self.frame_gametype.grid(row=0, column=1, sticky="n")
        self.radiobutton_gametype_computer.grid(row=1, column=0, sticky="w")
        self.radiobutton_gametype_online.grid(row=2, column=0, sticky="w")

        self.frame_ai.grid(row=0, column=2, sticky="n")
        self.optionmenu_ai.grid(row=0, column=0, sticky="w")
        self._layout_ai_settings()

        self.button_cancel.grid(row=1, column=0)
        self.button_start.grid(row=1, column=1)

    def _layout_ai_settings(self):
        ai = AIOption[self.ai_var.get()]
        if ai is AIOption.Randy:
            self.frame_ai_settings.grid_remove()
        elif ai is AIOption.Marty:
            self.frame_ai_settings.grid(row=1, column=0)
            self.label_depth.grid(row=0, column=0)
            self.spinbox_minmax_depth.grid(row=0, column=1)
        else:
            assert False

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
        _my_player = GUIPlayer(
            my_color,
            self.board_view.redraw,
            _show_winner,
        )

    def _make_opponent_player(self, color: Color):
        game_type = GameType[self.game_type_var.get()]
        if game_type == GameType.computer:
            OpponentPlayerClass = ai_options[AIOption[self.ai_var.get()]]
            _logger.debug(
                "%s chosen with settings %s",
                OpponentPlayerClass.__name__,
                self.ai_settings,
            )
            opponent = OpponentPlayerClass(color, **self.ai_settings)
        else:
            assert False, f"{game_type} not implemented"
        return opponent


def _show_winner(color: Optional[Color], _: Board):
    if color is None:
        msg = "The game is drawn!"
    else:
        msg = f"{color.name.capitalize()} has won!"
    tk.messagebox.showinfo("Game Over", msg)


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
