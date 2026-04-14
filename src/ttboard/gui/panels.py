import tkinter as tk
from tkinter import ttk
import logging
from functools import partial
from .tables import PropsTable
from .scroll import addScrollBar

log = logging.getLogger(__name__)

class CollectionRow(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
    def build(self, vc, suffix=''):
        lview = vc.vmodel.listView
        
        label = tk.Label(self, text='Collections: ')
        combobox = ttk.Combobox(self, values=None,
                                textvariable=lview.collection)
        combobox.bind('<<ComboboxSelected>>', vc.onCollectionSelected)

        jpathLabel = tk.Label(self, text='JSONPath: ')
        jpathText = tk.Entry(self, textvariable=lview.jsonPath)
        lview.jsonPath.set('$.*')

        vc.addWidget(f'collectionCBox{suffix}', combobox)
        vc.addWidget(f'listJpathText{suffix}', jpathText)
        
        label.pack(side=tk.LEFT)
        combobox.pack(side=tk.LEFT, fill=tk.X)
        jpathLabel.pack(side=tk.LEFT)
        jpathText.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
class PathRow(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
    def build(self, vc, suffix=''):
        fview = vc.vmodel.itemView
        
        jpathLabel = tk.Label(self, text='JSONPath: ')
        jpathText = tk.Entry(self, textvariable=fview.elementPath)

        vc.addWidget(f'objJpathText{suffix}', jpathText)

        jpathLabel.pack(side=tk.LEFT)
        jpathText.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
class EntryArray(tk.Frame):
    def __init__(self, master, n=0, **kwargs):
        super().__init__(master, **kwargs)
        self.n = n
        
    def build(self, vc):
        label = tk.Label(self, text='Filter conditions: ')
        label.pack(side=tk.LEFT)

        for i in range(self.n):
            entry = tk.Entry(self)
            entry.pack(side=tk.LEFT, expand=True)

class ListButtons(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
    def build(self, vc):
        button1 = ttk.Button(self, text='Run', width=8, command=vc.onListRun)
        button2 = ttk.Button(self, text='Filter', width=8)
        button3 = ttk.Button(self, text='Columns', width=8)
        button4 = ttk.Button(self, text='Save', width=8, command=vc.onListSave)
        button5 = ttk.Button(self, text='New entry', width=10, command=vc.onNewEntry)
        grid_styles = {
            'padx': 5,
            'pady': 2
            }
        button1.grid(row=0, column=0, **grid_styles)
        button2.grid(row=0, column=1, **grid_styles)
        button3.grid(row=0, column=2, **grid_styles)
        button4.grid(row=0, column=3, **grid_styles)
        button5.grid(row=0, column=4, **grid_styles)

class ObjectButtons(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
    def build(self, vc):
        self.button1 = ttk.Button(self, text='<', width=3)
        self.button2 = ttk.Button(self, text='>', width=3)
        self.button3 = ttk.Button(self, text='Save', width=6)
        grid_styles = {
            'padx': 5,
            'pady': 2
            }
        self.button1.grid(row=0, column=0, **grid_styles)
        self.button2.grid(row=0, column=1, **grid_styles)
        self.button3.grid(row=0, column=2, **grid_styles)
        
class ListPanel(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
    def build(self, vc, title, suffix=''):
        label = tk.Label(self, text=title)
        label.pack(anchor=tk.NW)
        collection = CollectionRow(self)
        buttons = ListButtons(self)
        tableFrame = tk.Frame(self)
        table = ttk.Treeview(tableFrame, columns=(1, 2, 3), show='headings')
        addScrollBar(table, scrollX=True, scrollY=True)

        listNumber = 1
        if suffix == '2':
            listNumber = 2
        table.bind('<Double-1>', partial(vc.onEntrySelected, listNumber))
        vc.addWidget(f'listTable{suffix}', table)
        
        collection.build(vc, suffix)
        buttons.build(vc)
        #table.build(vc)
        
        collection.pack(anchor=tk.NW, fill=tk.X)
        buttons.pack(anchor=tk.NW)
        tableFrame.pack(anchor=tk.NW, fill=tk.BOTH, expand=True)
        
class ObjectPanel(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def build(self, vc):
        fview = vc.vmodel.itemView
        
        label = tk.Label(self, text='Object view')
        jsonPath = PathRow(self)
        buttons = ObjectButtons(self)
        table = PropsTable(self, fview.useIncludeButton)

        #addScrollBar(table, scrollX=True, scrollY=True)
        #table.bind('<Double-1>', vc.onObjectTableEdit)
        
        vc.addWidget('objectTable', table)
        jsonPath.build(vc)
        buttons.build(vc)
        table.build(vc)
        
        label.pack(anchor=tk.NW)
        jsonPath.pack(side=tk.TOP, fill=tk.X)
        buttons.pack(side=tk.TOP, fill=tk.X)
        table.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        buttons.button3.bind('<Button-1>', vc.onSaveFields)

class MainPanel(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def build(self, vc):
        splitPanel = tk.PanedWindow(self, orient=tk.HORIZONTAL, bd=2, sashrelief=tk.GROOVE, height=400)

        twoListPanel = tk.PanedWindow(self, orient=tk.VERTICAL, bd=2, sashrelief=tk.GROOVE, height=200)
        self.listPanel = ListPanel(twoListPanel, bg='blue')
        self.listPanel2 = ListPanel(twoListPanel, bg='blue')
        twoListPanel.add(self.listPanel)
        twoListPanel.add(self.listPanel2)

        self.objectPanel = ObjectPanel(splitPanel, bg='green')
        self.listPanel.build(vc, title='List view')
        self.listPanel2.build(vc, title='2nd list view', suffix='2')
        self.objectPanel.build(vc)
        
        splitPanel.add(twoListPanel, width=800)
        splitPanel.add(self.objectPanel, width=300)

        splitPanel.pack(expand=True, fill=tk.BOTH)
        
