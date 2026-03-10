import tkinter as tk
from tkinter import ttk

class CollectionRow(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.build()
        
    def build(self):
        label = tk.Label(self, text='Collections: ')
        combobox = ttk.Combobox(self, values=None)
        jpathLabel = tk.Label(self, text='JSONPath: ')
        jpathText = tk.Entry(self)
        jpathText.insert(0, '$.')
        
        label.pack(side=tk.LEFT)
        combobox.pack(side=tk.LEFT, fill=tk.X)
        jpathLabel.pack(side=tk.LEFT)
        jpathText.pack(side=tk.LEFT)
        
class PathRow(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.build()
        
    def build(self):
        jpathLabel = tk.Label(self, text='JSONPath: ')
        jpathText = tk.Entry(self)
        jpathText.insert(0, '$.')
        
        jpathLabel.pack(side=tk.LEFT)
        jpathText.pack(side=tk.LEFT)
        
class EntryArray(tk.Frame):
    def __init__(self, master, n=0, **kwargs):
        super().__init__(master, **kwargs)
        self.n = n
        self.build()
        
    def build(self):
        label = tk.Label(self, text='Filter conditions: ')
        label.pack(side=tk.LEFT)

        for i in range(self.n):
            entry = tk.Entry(self)
            entry.pack(side=tk.LEFT, expand=True)

class ListTable(ttk.Treeview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.build()
        
    def build(self):
        table = ttk.Treeview(self, columns=(1, 2, 3), show='headings')
        table.pack(fill=tk.BOTH, expand=True)
        
class ListPanel(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.build()
        
    def build(self):
        label = tk.Label(self, text='List view')
        label.pack(anchor=tk.NW)
        collection = CollectionRow(self)
        inputs = EntryArray(self, n=5)
        table = ListTable(self)
        
        collection.pack(anchor=tk.NW)
        inputs.pack(anchor=tk.NW)
        table.pack(anchor=tk.NW, fill=tk.BOTH, expand=True)
        
class ObjectPanel(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.build()

    def build(self):
        label = tk.Label(self, text='Object view')
        jsonPath = PathRow(self)
        table = ListTable(self)
        
        label.pack(anchor=tk.NW)
        jsonPath.pack(anchor=tk.NW)
        table.pack(anchor=tk.NW, fill=tk.BOTH, expand=True)
        

class MainPanel(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.build()

    def build(self):
        splitPanel = tk.PanedWindow(self, orient=tk.HORIZONTAL, bd=2, sashrelief=tk.GROOVE)
        self.listPanel = ListPanel(splitPanel, bg='blue')
        self.objectPanel = ObjectPanel(splitPanel, bg='green')
        splitPanel.add(self.listPanel, width=800)
        splitPanel.add(self.objectPanel, width=300)

        splitPanel.pack(expand=True, fill=tk.BOTH)
        
