import tkinter as tk
from tkinter import ttk

class MenuBar(tk.Menu):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
    def build(self, vc):
        menu_File = tk.Menu(self, tearoff=0)
        self.add_cascade(label='File', menu=menu_File)

        menu_File.add_command(label='Open', command=vc.onFileOpen)
        menu_File.add_command(label='Save', command=vc.onFileSave)
        menu_File.add_command(label='SaveAs', command=vc.onFileSaveAs)
        menu_File.add_separator()
        menu_File.add_command(label='Quit', command=vc.onFileQuit)

        menu_Help = tk.Menu(self, tearoff=0)
        self.add_cascade(label='Help', menu=menu_Help)
        menu_Help.add_command(label='About', command=None)
