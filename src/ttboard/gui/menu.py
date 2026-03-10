import tkinter as tk
from tkinter import ttk

def show_open():
    print('File->Open')
    
def show_save():
    print('File->Save')
    
def show_saveAs():
    print('File->SaveAs')
    
def show_quit():
    print('File->Quit')
    
class MenuBar(tk.Menu):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.build()
        
    def build(self):
        menu_File = tk.Menu()
        self.add_cascade(label='File', menu=menu_File)

        menu_File.add_command(label='Open', command=show_open)
        menu_File.add_command(label='Save', command=show_save)
        menu_File.add_command(label='SaveAs', command=show_saveAs)
        menu_File.add_separator()
        menu_File.add_command(label='Quit', command=show_quit)
