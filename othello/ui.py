import tkinter as tk
import logging

_LOGGER = logging.getLogger(__name__)


class BoardView:
    def __init__(self, master):
        self.cell_size = 40
        self.border_width = 3
        self.grid_line_width = 2
        self.canvas = tk.Canvas(
            master,
            width=self.cell_size * 8 + self.grid_line_width * 7 - 1,
            height=self.cell_size * 8 + self.grid_line_width * 7 - 1,
            borderwidth=f'{self.border_width}',
            relief='raised',
            bg='#000'
        )
        self.canvas.pack()
        self.canvas.bind('<Button-1>', BoardView.on_click)
        self.redraw()

    @staticmethod
    def on_click(event):
        _LOGGER.info(event)

    def redraw(self):
        for r in range(8):
            for c in range(8):
                col_off = c * self.grid_line_width + self.border_width
                row_off = r * self.grid_line_width + self.border_width
                self.canvas.create_rectangle(
                    c * self.cell_size + col_off,
                    r * self.cell_size + row_off,
                    (c + 1) * self.cell_size + col_off,
                    (r + 1) * self.cell_size + row_off,
                    fill='#060'
                )


def init(root: tk.Tk):
    root.title('Othello')
    root.after()

    main = tk.Frame(root)
    main.pack_configure(expand=True, fill='both')
    board_view = BoardView(main)


def loop():
    root = tk.Tk()
    init(root)
    root.mainloop()
