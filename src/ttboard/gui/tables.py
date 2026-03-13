import tkinter as tk
from tkinter import ttk
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

    def valueWidget(self, value):
        w = None
        bgcolor = 'white smoke'
        tvalue = type(value)
        if tvalue in (int, float, str):
            w = tk.Entry(self, bg=bgcolor)
            w.insert(0, value)
        elif tvalue == list:
            w = ttk.Button(self, text='Show list', style='objOn.TButton')
        elif tvalue == dict:
            w = ttk.Button(self, text='Open object', style='objOn.TButton')
        return w
    
    def addField(self, irow, field):
        log.info(f'addField {field}')
        bgcolor = 'white smoke'
        key, included, value = field
        image = None
        if included:
            image = self.images['CheckBoxChecked']
        else:
            image = self.images['EmptyCheckBox']
            bgcolor = 'light gray'

        log.info(f'  add field {field}')
        log.info(f'    value: {value}')
        image0 = tk.Label(self, image=image, bg=bgcolor)
        label1 = tk.Label(self, text=key, bg=bgcolor)
        w2 = self.valueWidget(value)
        
        col0 = 0
        if self.useInclude:
            image0.grid(row=irow, column=0, sticky=tk.NSEW)
            col0 = 1
        label1.grid(row=irow, column=col0+0, sticky=tk.NSEW)
        w2.grid(row=irow, column=col0+1, sticky=tk.NSEW)
        
            
    def updateFields(self, fields):
        self.clear()
        log.info(f'Update {len(fields)} fields')
        for irow, field in enumerate(fields):
            self.addField(irow+1, field)
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
        self.rows = []
    
