import tkinter as tk
from .menu import MenuBar
from .panels import MainPanel
from .footer import Footer


class MainWindow(tk.Frame):
    def __init__(self, master=None, viewControl=None, **kwargs):
        super().__init__(master, **kwargs)
        self.vc = viewControl

        self.build()
        
    def build(self):
        self.pack(fill=tk.BOTH, expand=True)

        self.menubar = MenuBar(self)
        self.master.configure(menu=self.menubar)
        
        self.mainPanel = MainPanel(self, bg='red')
        self.footer = Footer(self, text='Footer', bg='yellow')

        self.mainPanel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.footer.pack(side=tk.BOTTOM, fill=tk.X)
