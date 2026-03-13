import tkinter as tk
from tkinter import ttk

def addScrollBar(widget, scrollX=True, scrollY=True):
    frame = widget.master
    if scrollX:
        xScroll = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=widget.xview)
        widget.configure(xscrollcommand=xScroll.set)
        xScroll.pack(side=tk.TOP, fill=tk.X)
    if scrollY:
        yScroll = tk.Scrollbar(frame, orient=tk.VERTICAL, command=widget.yview)
        widget.configure(yscrollcommand=yScroll.set)
        yScroll.pack(side=tk.RIGHT, fill=tk.Y)
    widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    return frame
