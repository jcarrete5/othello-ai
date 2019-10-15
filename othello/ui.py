import tkinter as tk
import tkinter.ttk as ttk
import asyncio

_running = True

class App(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        self.title_lbl = ttk.Label(text='Othello')
        self.title_lbl.grid(row=0, column=0)
        # self.othello_frame = ttk.Frame(self, )

def stop():
    global _running
    _running = False

async def loop(interval=1/20):
    global _running
    root = tk.Tk()
    # pylint: disable=unused-variable
    app = App(root)
    while _running:
        root.update()
        await asyncio.sleep(interval)
