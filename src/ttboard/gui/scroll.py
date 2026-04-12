import tkinter as tk
from tkinter import ttk

def addScrollBar(widget, scrollX=True, scrollY=True):
    frame = widget.master
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    widget.grid(row=0, column=0, sticky=tk.NSEW)
    if scrollY:
        yScroll = tk.Scrollbar(frame, orient=tk.VERTICAL, command=widget.yview)
        widget.configure(yscrollcommand=yScroll.set)
        yScroll.grid(row=0, column=1, sticky=tk.NS)
    if scrollX:
        xScroll = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=widget.xview)
        widget.configure(xscrollcommand=xScroll.set)
        xScroll.grid(row=1, column=0, sticky=tk.EW)
    return frame
