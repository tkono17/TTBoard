import os
import tkinter as tk
from tkinter import filedialog
import logging
import re

log = logging.getLogger(__name__)


class ViewControl:
    def __init__(self, gui, app):
        self.gui = gui
        self.app = app

        # GUI widgets
        self.widgets = {}

        self.fileTypes = [ ('JSON file', '*.json'), ('', '*') ]
        self.fileDirName = os.getcwd()

        # Data related to a list
        self.selectorNames = []
        self.selectedCollection = None
        self.listJsonPath = tk.StringVar(value='$.')
        self.listEntries = []
        self.listColumnStatus = []
        
        # Data related to an object
        self.objectJsonPath = tk.StringVar(value='$.')
        self.objectProperties = {}
        pass

    def addWidget(self, wname, w):
        self.widgets[wname] = w
        log.info(f'  Added widget {wname}')

    def findWidget(self, wname):
        w = None
        log.info(f'  widget names: {self.widgets.keys()}')
        if wname in self.widgets.keys():
            w = self.widgets[wname]
            log.info(f'  widget is {w}')
        else:
            log.warning(f'  widget not found {self.widgets.items()}')
        return w
        
    def updateCollections(self):
        self.selectorNames = list(map(lambda x: x.name, self.app.selectors))
        self.gui.mainPanel.listPanel
        w = self.findWidget('collectionCBox')
        if w:
            w['values'] = self.selectorNames
        else:
            log.warning(f'  Widget collectionCBox was not found')

    def addTableRow(self, table, values):
        table.insert('', 'end', values=values)
        
    def updateListTable(self):
        def valuesIn(entry):
            values, etype = [], type(entry)
            if etype == dict:
                keys = entry.keys()
                for cname in columns:
                    if cname in keys:
                        values.append(entry[cname])
                    else:
                        values.append('')
            elif etype in (int, float, str):
                values = [ entry ]
            else:
                log.warning('Do not know how to get value from {etype}')
            return values
        
        nentries = len(self.listEntries)
        ncolumns = len(self.listColumns)
        log.info(f'List table {nentries} entries with {ncolumns} columns')

        columns = [ x[0] for x in filter(lambda y: y[1], self.listColumns)]
        tree = self.findWidget('listTable')
        if tree:
            tree.delete(*tree.get_children())

            tree.config(columns=columns, show='headings')
            for column in columns:
                tree.column(column, width=100, anchor='center')
                tree.heading(column, text=column, anchor='center')
            for entry in self.listEntries:
                values = valuesIn(entry)
                self.addTableRow(tree, values)
    #--------------------------------------------------------------------
    # Action handlers
    #--------------------------------------------------------------------
    def onFileOpen(self):
        log.info('File->Open')
        fn = filedialog.askopenfilename(filetypes=self.fileTypes,
                                        initialdir=self.fileDirName)
        self.fileDirName = os.path.dirname(fn)
        self.app.openJsonFile(fn)
        self.updateCollections()
    
    def onFileSave(self):
        print('File->Save')
    
    def onFileSaveAs(self):
        print('File->SaveAs')
    
    def onFileQuit(self):
        print('File->Quit')

    def onCollectionSelected(self, event):
        self.selectedCollection = event.widget.get()
        selector = self.app.findSelector(self.selectedCollection)
        if selector:
            self.listJsonPath.set(selector.jsonPath)
        else:
            self.listJsonPath.set('$.')

    def onListRun(self):
        args = re.findall('\[(.*?)\]', self.listJsonPath.get())
        v = self.app.getList(self.selectedCollection, *args)
        if v is None:
            self.listEntries = []
        else:
            self.listEntries = v
        selector = self.app.findSelector(self.selectedCollection)
        if selector:
            cls = selector.elementType
            self.listElementType = cls
            if hasattr(cls, '__dataclass_fields__'):
                self.listColumns = [ (x, True) for x 
                                     in cls.__dataclass_fields__.keys()]
            elif cls in (int, float, str):
                self.listColumns = [ ('Value', True) ]
            else:
                log.warning(f'Do not know how to handle type {cls}')
        else:
            self.listElementType = None
            self.listColumns = []
        self.updateListTable()
