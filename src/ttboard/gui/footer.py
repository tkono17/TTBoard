import tkinter as tk

class Footer(tk.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def build(self, vc):
        vc.addWidget('footer', self)
    
