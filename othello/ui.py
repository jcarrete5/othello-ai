from __future__ import annotations
import tkinter as tk
import logging
from typing import TYPE_CHECKING
from othello import bitboard as bb

if TYPE_CHECKING:
    from othello.game import BoardState

_LOGGER = logging.getLogger(__name__)


class BoardView:
    def __init__(self, master, board_state: BoardState):
        self.board_state = board_state
        self.cell_size = 40
        self.border_width = 3
        self.grid_line_width = 1
        self.canvas = tk.Canvas(
            master,
            width=self.cell_size * 8 + self.grid_line_width * 7 - 1,
            height=self.cell_size * 8 + self.grid_line_width * 7 - 1,
            borderwidth=f'{self.border_width}',
            highlightthickness=0,
            relief=tk.RAISED,
            bg='#000'
        )
        self.canvas.pack()
        self.canvas.bind('<Button-1>', BoardView.on_click)
        _LOGGER.debug('Canvas dim (%d, %d)',
                      self.canvas.winfo_reqwidth(),
                      self.canvas.winfo_reqheight())
        self.redraw(board_state.white, board_state.black)

    @staticmethod
    def on_click(event):
        _LOGGER.debug(event)

    def redraw(self, white: int, black: int):
        _LOGGER.debug('Redrawing Board with white=%0#16x, black=%0#16x', white, black)
        self.canvas.delete(tk.ALL)
        for r in range(8):
            for c in range(8):
                x_off = c * self.cell_size + c * self.grid_line_width + self.border_width - 1
                y_off = r * self.cell_size + r * self.grid_line_width + self.border_width - 1
                # Draw green empty cell
                self.canvas.create_rectangle(
                    x_off,
                    y_off,
                    self.cell_size + x_off,
                    self.cell_size + y_off,
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
                    self.canvas.create_oval(
                        x_off + inset,
                        y_off + inset,
                        x_off + self.cell_size - inset,
                        y_off + self.cell_size - inset,
                        fill=fill_color)


def init_widgets(root: tk.Tk, board_state: BoardState):
    root.title('Othello')

    main = tk.Frame(root)
    main.pack_configure(expand=True, fill='both')
    board_view = BoardView(main, board_state)
    board_state.onchange(lambda w, b: root.after(0, board_view.redraw(w, b)))

def loop(board_state: BoardState):
    _LOGGER.info('Init ui loop')
    root = tk.Tk()
    init_widgets(root, board_state)
    root.mainloop()
    _LOGGER.info('Quit ui loop')
