import tkinter as tk

root = tk.Tk()

class MainWindow(tk.Frame):
    def __init__(self, master=None, viewControl=None, **kwargs):
        super().__init__(master, **kwargs)
        self.vc = viewControl
        self.pack()

        

    
