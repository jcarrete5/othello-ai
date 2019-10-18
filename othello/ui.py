import tkinter as tk
import logging

_LOGGER = logging.getLogger(__name__)


class BoardView:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=400, height=400, bg='#060')
        self.canvas.grid(row=0, column=0)


def init(root: tk.Tk):
    root.title('Othello')
    root.geometry('800x600')

    main = tk.Frame(root)
    main.pack_configure(expand=True, fill='both')
    board_view = BoardView(main)


def loop():
    root = tk.Tk()
    init(root)
    root.mainloop()
