import tkinter as tk
from tkinter import ttk
from functools import partial
import logging
from ..tools import openAssetImage

log = logging.getLogger(__name__)

class PropsTable(tk.Frame):
    def __init__(self, master, useInclude=False, **kwargs):
        super().__init__(master, **kwargs)
        self.useInclude = useInclude
        self.images = {
            'EmptyCheckBox': openAssetImage('EmptyCheckBox.png'),
            'CheckBoxChecked': openAssetImage('CheckBoxChecked.png'),
            }
        self.headings = None
        self.rows = []

    def valueWidget(self, var, vc):
        w = None
        bgcolor = 'white smoke'
        tvalue = type(var)
        if var is None:
            w = tk.Entry(self)
        elif tvalue == tk.StringVar:
            w = tk.Entry(self, textvariable=var, bg=bgcolor)
            var.trace_add('write', vc.onFieldChanged)
        elif tvalue == list:
            w = ttk.Button(self, text='Show list', style='objOn.TButton')
        elif tvalue == dict:
            w = ttk.Button(self, text='Show object', style='objOn.TButton')
        else:
            log.warning(f'  Unexpected variable type in the row entry {tvalue}')
            w = tk.Entry(self)
        return w
    
    def addField(self, irow, row_data, vc):
        #log.info(f'addField {row_data}')
        bgcolor = 'white smoke'
        included, key, value = row_data.isActive, row_data.name, row_data.value
        image = None
        if included:
            image = self.images['CheckBoxChecked']
        else:
            image = self.images['EmptyCheckBox']
            bgcolor = 'light gray'

        image0 = tk.Label(self, image=image, bg=bgcolor)
        label1 = tk.Label(self, text=key, bg=bgcolor)
        w2 = self.valueWidget(value, vc)
        
        col0 = 0
        if self.useInclude:
            image0.grid(row=irow, column=0, sticky=tk.NSEW)
            col0 = 1
        label1.grid(row=irow, column=col0+0, sticky=tk.NSEW)
        w2.grid(row=irow, column=col0+1, sticky=tk.NSEW)

        image0.bind('<Button-1>', partial(vc.onFieldClicked, irow-1))
            
    def updateFields(self, rows_data, vc):
        self.clear()
        #log.info(f'Update {len(rows_data)} fields')
        for irow, row_data in enumerate(rows_data):
            self.addField(irow+1, row_data, vc)
        pass
    
    def buildHeadings(self):
        col0 = 0
        if self.useInclude:
            label0 = tk.Label(self, text='Include')
            label0.grid(row=0, column=0)
            col0 = 1
        label1 = tk.Label(self, text='Field')
        label2 = tk.Label(self, text='Value')
        label1.grid(row=0, column=col0+0)
        label2.grid(row=0, column=col0+1)
        
    def build(self, vc):
        self.buildHeadings()
        pass
    
    def clear(self):
        for row in self.rows:
            row.destroy()
        for w in self.winfo_children():
            w.destroy()
        self.rows = []
    
