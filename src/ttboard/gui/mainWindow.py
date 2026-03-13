import tkinter as tk
from tkinter import ttk
from .menu import MenuBar
from .panels import MainPanel
from .footer import Footer


class MainWindow(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.vc = None
        self.style = ttk.Style()
        self.setStyles()

    def setStyles(self):
        self.style.theme_use('clam')
        self.style.configure('objOn.TButton', background='SeaGreen2', foreground='navy')
        
    def build(self, vc):
        self.vc = vc
        
        self.pack(fill=tk.BOTH, expand=True)

        self.menuBar = MenuBar(self)
        self.master.configure(menu=self.menuBar)
        self.menuBar.build(vc)
        
        self.mainPanel = MainPanel(self, bg='red')
        self.mainPanel.build(vc)
        self.footer = Footer(self, text='Footer', bg='yellow')
        self.footer.build(vc)
        
        self.mainPanel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.footer.pack(side=tk.BOTTOM, fill=tk.X)
