import tkinter as tk
import tkinter.ttk as ttk

class App(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        self.title_lbl = ttk.Label(text='Othello')
        self.title_lbl.grid(row=0, column=0)
        # self.othello_frame = ttk.Frame(self, )

async def loop():
    root = tk.Tk()
    # pylint: disable=unused-variable
    app = App(root)
    root.mainloop()