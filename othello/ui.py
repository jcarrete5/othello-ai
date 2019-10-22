from __future__ import annotations
import tkinter as tk
import tkinter.messagebox
import logging
from random import choice as chooseFrom
from typing import TYPE_CHECKING
from othello import bitboard as bb
from othello.game import Game, GameType, BoardState
from othello.player import Color


_LOGGER = logging.getLogger(__name__)
# pylint: disable=invalid-name
_game = None


class BoardView(tk.Canvas):
    def __init__(self, master):
        self._cell_size = 40
        self._border_width = 3
        self._grid_line_width = 1
        super().__init__(
            master,
            width=self._cell_size * 8 + self._grid_line_width * 7 - 1,
            height=self._cell_size * 8 + self._grid_line_width * 7 - 1,
            borderwidth=f'{self._border_width}',
            highlightthickness=0,
            relief=tk.RAISED,
            bg='#000'
        )
        self.pack()
        self.bind('<Button-1>', BoardView.on_click)

        self._board_state = None
        _LOGGER.debug('Canvas dim (%d, %d)',
                      self.winfo_reqwidth(),
                      self.winfo_reqheight())
        self._redraw()

    @property
    def board_state(self) -> BoardState:
        return self._board_state

    @board_state.setter
    def board_state(self, value: BoardState):
        self._board_state = value
        self.after(0, self._redraw)

    @staticmethod
    def on_click(event):
        _LOGGER.debug(event)

    def _redraw(self):
        if self.board_state is not None:
            white = self.board_state.white
            black = self.board_state.black
            _LOGGER.debug('Redrawing Board with white=%0#16x, black=%0#16x', white, black)
        self.delete(tk.ALL)
        for r in range(8):
            for c in range(8):
                x_off = c * self._cell_size + c * self._grid_line_width + self._border_width - 1
                y_off = r * self._cell_size + r * self._grid_line_width + self._border_width - 1
                # Draw green empty cell
                self.create_rectangle(
                    x_off,
                    y_off,
                    self._cell_size + x_off,
                    self._cell_size + y_off,
                    fill='#060'
                )

                if self.board_state is not None:
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
    def __init__(self, parent, board_view: BoardView):
        super().__init__(parent)
        self.transient(parent)
        self.focus_set()
        self.grab_set()
        self.title('New Game')
        self.board_view = board_view

        frame = tk.Frame(self)
        frame.pack_configure(expand=True)
        self.foe_var = tk.Variable(frame, GameType.COMPUTER)
        self.color_var = tk.Variable(frame, Color.BLACK)
        oppenent_frame = tk.LabelFrame(frame, text='Opponent')
        oppenent_frame.grid(row=0, column=0, sticky='n')
        tk.Radiobutton(oppenent_frame, text='Computer', variable=self.foe_var, value=GameType.COMPUTER).grid(
            row=1, column=0, sticky='w'
        )
        tk.Radiobutton(oppenent_frame, text='Online', variable=self.foe_var, value=GameType.ONLINE, state=tk.DISABLED).grid(
            row=2, column=0, sticky='w'
        )
        color_frame = tk.LabelFrame(frame, text='Color')
        color_frame.grid(row=0, column=1, sticky='n')
        tk.Radiobutton(color_frame, text='Black', variable=self.color_var, value=Color.BLACK).grid(
            row=1, column=1, sticky='w'
        )
        tk.Radiobutton(color_frame, text='White', variable=self.color_var, value=Color.WHITE).grid(
            row=2, column=1, sticky='w'
        )
        tk.Radiobutton(color_frame, text='Random', variable=self.color_var, value=None).grid(
            row=3, column=1, sticky='w'
        )
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
        global _game

        if _game is not None:
            proceed = tk.messagebox.askokcancel('Start New Game', 'Another game is already in progress. Proceed?')
            if not proceed:
                self.destroy()

        state = BoardState(
            init_white=0x0000001008000000,
            init_black=0x0000000810000000,
            turn_player_color=self.color_var.get() or chooseFrom(list(Color))
        )
        self.board_view.board_state = state
        if _game:
            _game.interrupt()
        _game = Game(state)
        _game.start()
        self.destroy()


def init_widgets(root: tk.Tk):
    root.title('Othello')

    main = tk.Frame(root)
    main.pack_configure(expand=True, fill='both')
    board_view = BoardView(main)

    menubar = tk.Menu(root)
    gamemenu = tk.Menu(menubar, tearoff=0)
    gamemenu.add_command(label='New Game...', command=lambda: NewGameDialog(root, board_view))
    menubar.add_cascade(label='Game', menu=gamemenu)
    root.config(menu=menubar)


def loop():
    _LOGGER.info('Init ui loop')
    root = tk.Tk()
    init_widgets(root)
    root.mainloop()
    global _game
    if _game is not None:
        _game.interrupt()
        _game.join()
    _LOGGER.info('Quit ui loop')
