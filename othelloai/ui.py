"""
UI for the othello application.
"""
from __future__ import annotations
import tkinter as tk
import tkinter.messagebox  # pylint: disable=unused-import
import logging
from queue import Queue, Empty as QueueEmpty
from random import choice as chooseFrom
from . import bitboard as bb
from .game import Game, GameType, EventName, BoardState
from .player import Color


EVENT_QUEUE = Queue()
_EVENT_SUBSCRIPTIONS = dict()
_LOGGER = logging.getLogger(__name__)
_game = None  # pylint: disable=invalid-name


class BoardView(tk.Canvas):
    """ Represents the state of the board graphically. """
    def __init__(self, master):
        self._cell_size = 40
        self._border_width = 0
        self._grid_line_width = 1
        super().__init__(
            master,
            width=self._cell_size * 8 + self._grid_line_width * 7,
            height=self._cell_size * 8 + self._grid_line_width * 7,
            borderwidth=f'{self._border_width}',
            highlightthickness=0,
            bg='#000'
        )
        self.pack()
        self.bind('<Button-1>', self.onclick)

        self._board_state = None
        _LOGGER.debug('Canvas dim (%d, %d)',
                      self.winfo_reqwidth(),
                      self.winfo_reqheight())
        _subscribe(EventName.BOARD_CHANGED, self._redraw)
        self._redraw(0, 0)

    def onclick(self, event):
        _LOGGER.debug('BoardView clicked %s', event)
        if _game is None:
            return
        col = (event.x - self._border_width) / self.winfo_reqwidth() * 8
        row = (event.y - self._border_width) / self.winfo_reqheight() * 8
        _LOGGER.debug('(row=%f, col=%f)', row, col)
        _LOGGER.debug('(row=%d, col=%d)', row, col)
        if 0 <= col < 8 and 0 <= row < 8:
            move = bb.Position(int(row), int(col))
            if move in _game.board_state.valid_moves():
                _game.my_player.move = move
            else:
                _LOGGER.info('%s played an invalid move', _game.my_player)

    def _redraw(self, white: int, black: int):
        _LOGGER.debug('Redrawing Board with white=%0#16x, black=%0#16x', white, black)
        self.delete(tk.ALL)
        for r in range(8):
            for c in range(8):
                x_off = c * self._cell_size + c * self._grid_line_width + self._border_width
                y_off = r * self._cell_size + r * self._grid_line_width + self._border_width
                # Draw green empty cell
                self.create_rectangle(
                    x_off,
                    y_off,
                    self._cell_size + x_off,
                    self._cell_size + y_off,
                    fill='#060'
                )

                # Draw piece in cell
                mask = bb.pos_mask(r, c)
                inset = 5
                fill_color = None
                if white & mask != 0:
                    fill_color = '#fff'
                elif black & mask != 0:
                    fill_color = '#000'
                if fill_color:
                    self.create_oval(
                        x_off + inset,
                        y_off + inset,
                        x_off + self._cell_size - inset,
                        y_off + self._cell_size - inset,
                        fill=fill_color)


class NewGameDialog(tk.Toplevel):
    """ Modal dialog window for creating new games. """
    def __init__(self, parent, board_view: BoardView):
        super().__init__(parent)
        self.transient(parent)
        self.focus_set()
        self.grab_set()
        self.title('New Game')
        x = int(parent.winfo_rootx() + parent.winfo_width() / 2 - self.winfo_reqwidth() / 2)
        y = int(parent.winfo_rooty() + parent.winfo_height() / 2 - self.winfo_reqheight() / 2)
        self.geometry(f'+{x}+{y}')
        self.board_view = board_view

        frame = tk.Frame(self)
        frame.pack_configure(expand=True)
        self.game_type = tk.StringVar(frame, GameType.COMPUTER.name)
        self.color_var = tk.StringVar(frame, Color.BLACK.name)
        oppenent_frame = tk.LabelFrame(frame, text='Opponent')
        oppenent_frame.grid(row=0, column=0, sticky='n')
        tk.Radiobutton(
            oppenent_frame,
            text='Computer',
            variable=self.game_type,
            value=GameType.COMPUTER.name
        ).grid(row=1, column=0, sticky='w')
        tk.Radiobutton(
            oppenent_frame,
            text='Online',
            variable=self.game_type,
            value=GameType.ONLINE.name,
            state=tk.DISABLED
        ).grid(row=2, column=0, sticky='w')
        color_frame = tk.LabelFrame(frame, text='Color')
        color_frame.grid(row=0, column=1, sticky='n')
        tk.Radiobutton(
            color_frame,
            text='Black',
            variable=self.color_var,
            value=Color.BLACK.name
        ).grid(row=1, column=1, sticky='w')
        tk.Radiobutton(
            color_frame,
            text='White',
            variable=self.color_var,
            value=Color.WHITE.name
        ).grid(row=2, column=1, sticky='w')
        tk.Radiobutton(
            color_frame,
            text='Random',
            variable=self.color_var,
            value=None
        ).grid(row=3, column=1, sticky='w')
        tk.Button(frame, text='Cancel', command=self.cancel).grid(row=1, column=0)
        tk.Button(frame, text='Start', command=self.submit).grid(row=1, column=1)
        self.bind('<Escape>', lambda e: self.cancel())
        self.bind('<Return>', lambda e: self.submit())
        self.wait_window(self)
        _LOGGER.debug('NewGameDialog closed')

    def cancel(self):
        _LOGGER.debug('Cancel')
        self.destroy()

    def submit(self):
        _LOGGER.debug('Submit')
        global _game  # pylint: disable=invalid-name

        if _game is not None:
            proceed = tk.messagebox.askokcancel(
                title='Start New Game',
                message='Another game is already in progress. Proceed?'
            )
            if not proceed:
                self.destroy()

        state = BoardState(
            init_white=0x0000001008000000,
            init_black=0x0000000810000000,
            turn_player_color=Color.BLACK
        )
        self.board_view.board_state = state
        if _game:
            _game.interrupt()
        _game = Game(
            state,
            self.color_var.get() and Color[self.color_var.get()] or chooseFrom(list(Color)),
            GameType[self.game_type.get()],
            EVENT_QUEUE
        )
        _game.start()
        self.destroy()


def _subscribe(name: EventName, callback):
    """ Add a callback for event name `name`. """
    if name in _EVENT_SUBSCRIPTIONS:
        _EVENT_SUBSCRIPTIONS[name].append(callback)
    else:
        _EVENT_SUBSCRIPTIONS[name] = [callback]


def _poll_queue(root: tk.Tk):
    """ Periodically poll the event queue for messages. """
    try:
        event_name, *args = EVENT_QUEUE.get_nowait()
    except QueueEmpty:
        pass
    else:
        if event_name in _EVENT_SUBSCRIPTIONS:
            for callback in _EVENT_SUBSCRIPTIONS[event_name]:
                callback(*args)
        else:
            _LOGGER.warning('Unhandled event %r with args %s', event_name, args)
    root.after(100, _poll_queue, root)


def _init_widgets(root: tk.Tk):
    root.title('Othello')

    main = tk.Frame(root)
    main.pack_configure(expand=True)
    board_view = BoardView(main)

    menubar = tk.Menu(root)
    gamemenu = tk.Menu(menubar, tearoff=0)
    gamemenu.add_command(label='New Game...', command=lambda: NewGameDialog(root, board_view))
    menubar.add_cascade(label='Game', menu=gamemenu)
    root.config(menu=menubar)


def loop():
    _LOGGER.info('Init ui loop')
    try:
        root = tk.Tk()
        _init_widgets(root)
        root.after(100, _poll_queue, root)
        root.mainloop()
        global _game  # pylint: disable=invalid-name
        if _game is not None:
            _game.interrupt()
            _game.join()
    finally:
        _LOGGER.info('Quit ui loop')
