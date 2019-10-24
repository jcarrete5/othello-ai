from __future__ import annotations
import tkinter as tk
import tkinter.messagebox  # pylint: disable=unused-import
import logging
from random import choice as chooseFrom
from othello import bitboard as bb
from othello.game import Game, GameType, BoardState
from othello.player import Color


_LOGGER = logging.getLogger(__name__)
_game = None  # pylint: disable=invalid-name


class BoardView(tk.Canvas):
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
        self._redraw(0, 0)

    @property
    def board_state(self) -> BoardState:
        return self._board_state

    @board_state.setter
    def board_state(self, value: BoardState):
        self._board_state = value
        self._board_state.onchange(lambda w, b: self.after(0, self._redraw(w, b)))
        self.after(0, lambda: self._redraw(self.board_state.white, self.board_state.black))

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
            if move in self.board_state.valid_moves():
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
        global _game

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
            Color[self.color_var.get()] or chooseFrom(list(Color)),
            GameType[self.game_type.get()]
        )
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
