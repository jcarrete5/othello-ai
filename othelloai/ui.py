"""UI for the othello application."""

import logging
import threading
import tkinter as tk
import tkinter.messagebox
from queue import Empty as QueueEmpty
from queue import Queue
from random import choice as choose_from
from typing import Optional

import ai
from . import bitboard as bb
from .game import BoardState, EventType, Game, GameType
from .player import Color, make_local_player, Player

event_queue = Queue()
_event_subscriptions = dict()
_logger = logging.getLogger(__name__)
_game: Optional[Game] = None
_my_player: Optional[Player] = None
_ui_reset_event = threading.Event()


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

        self._board_state = None
        _logger.debug(
            "Canvas dim (%d, %d)", self.winfo_reqwidth(), self.winfo_reqheight()
        )
        _subscribe(EventType.board_changed, self._redraw)
        self._redraw(0, 0)

    def onclick(self, event):
        _logger.debug("BoardView clicked %s", event)

        if _game is None:
            return

        col = (event.x - self._border_width) / self.winfo_reqwidth() * 8
        row = (event.y - self._border_width) / self.winfo_reqheight() * 8
        _logger.debug("(row=%f, col=%f)", row, col)
        _logger.debug("(row=%d, col=%d)", row, col)
        if 0 <= col < 8 and 0 <= row < 8:
            pos = bb.Position(int(row), int(col))
            if pos in _game.board_state.valid_moves():
                _my_player.make_move(pos)
            else:
                _logger.info("%s played an invalid move", _my_player)

    def _redraw(self, white: int, black: int):
        _logger.debug("Redrawing Board with white=%0#16x, black=%0#16x", white, black)
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
                if white & mask != 0:
                    fill_color = "#fff"
                elif black & mask != 0:
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
        x = int(
            parent.winfo_rootx() + parent.winfo_width() / 2 - self.winfo_reqwidth() / 2
        )
        y = int(
            parent.winfo_rooty()
            + parent.winfo_height() / 2
            - self.winfo_reqheight() / 2
        )
        self.geometry(f"+{x}+{y}")
        self.board_view = board_view

        frame = tk.Frame(self)
        frame.pack_configure(expand=True)
        self.game_type = tk.StringVar(frame, GameType.computer.name)
        self.color_var = tk.StringVar(frame, Color.BLACK.name)
        opponent_frame = tk.LabelFrame(frame, text="Opponent")
        opponent_frame.grid(row=0, column=0, sticky="n")
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
        color_frame = tk.LabelFrame(frame, text="Color")
        color_frame.grid(row=0, column=1, sticky="n")
        tk.Radiobutton(
            color_frame, text="Black", variable=self.color_var, value=Color.BLACK.name
        ).grid(row=1, column=1, sticky="w")
        tk.Radiobutton(
            color_frame, text="White", variable=self.color_var, value=Color.WHITE.name
        ).grid(row=2, column=1, sticky="w")
        tk.Radiobutton(
            color_frame, text="Random", variable=self.color_var, value=None
        ).grid(row=3, column=1, sticky="w")
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
        global _my_player

        state = BoardState(
            init_white=0x0000001008000000,
            init_black=0x0000000810000000,
            turn_player_color=Color.BLACK,
        )
        self.board_view.board_state = state

        my_color = (
            self.color_var.get()
            and Color[self.color_var.get()]
            or choose_from(list(Color))
        )
        _my_player = make_local_player(my_color, _ui_reset_event)

        if _game is not None:
            _ui_reset_event.set()
            _game.shutdown()
            _ui_reset_event.clear()

        _game = Game(
            state,
            _my_player,
            GameType[self.game_type.get()],
            event_queue,
            ai.random,  # TODO: Allow the user to select this
        )
        _game.start()


def _subscribe(name: EventType, callback):
    """Add a callback for event name `name`."""
    if name in _event_subscriptions:
        _event_subscriptions[name].append(callback)
    else:
        _event_subscriptions[name] = [callback]


def _poll_queue(root: tk.Tk):
    """Periodically poll the event queue for messages."""
    try:
        event_name, *args = event_queue.get_nowait()
    except QueueEmpty:
        pass
    else:
        if event_name in _event_subscriptions:
            for callback in _event_subscriptions[event_name]:
                callback(*args)
        else:
            _logger.warning("Unhandled event %r with args %s", event_name, args)
    root.after(100, _poll_queue, root)


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

    _logger.info("Init ui loop")

    try:
        root = tk.Tk()
        _init_widgets(root)
        root.after(100, _poll_queue, root)
        root.mainloop()
    finally:
        _ui_reset_event.set()
        if _game is not None:
            _game.shutdown()
