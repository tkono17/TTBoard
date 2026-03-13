import os
import tkinter as tk
from tkinter import filedialog
import logging
import re
from .tableManager import TableManager, FieldManager

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
        self.listColumns = []
        self.listStyle = 'table'
        
        # Data related to an object
        self.useIncludeButton = True
        self.objectJsonPath = tk.StringVar(value='$.')
        self.objectKey = None
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

    def updateTableEntries(self, table, tableMgr):
        if table:
            table.delete(*table.get_children())
            ocolumns = tableMgr.orderedColumns()
            log.info(f'  ordered columns: {ocolumns}')

            table.config(show='tree headings', columns=ocolumns)
            for heading in ocolumns:
                table.heading(heading, text=heading)
                table.column(heading, stretch=tk.NO)

            table.heading('#0', text='Icon')
            table.column('#0', minwidth=50, width=60, stretch=tk.NO)
            entries = tableMgr.getEntries()
            for values, image in entries:
                if image is not None:
                    log.info('Insert with image')
                    table.insert('', 'end', image=image, values=values)
                else:
                    log.info('Insert just values')
                    table.insert('', 'end', values=values)
        pass
    
    def updateFieldEntries(self, table, fieldMgr):
        fields = fieldMgr.getFields()
        table.updateFields(fields)
        pass
    
    def updateListTable(self):
        tree = self.findWidget('listTable')
        columnsEn = [ x[0] for x in filter(lambda y: y[1], self.listColumns)]
        if self.listStyle == 'table':
            allColumns = list(map(lambda x: x[0], self.listColumns))
            self.listTableMgr = TableManager(columnsEn,
                                             self.listEntries,
                                             allColumns=allColumns,
                                             useDeleteButton=True)
            self.updateTableEntries(tree, self.listTableMgr)
        elif self.listStyle == 'board':
            self.updateBoardEntries(tree, self.listEntries, columnsEn)

    def updateObject(self, jpath, obj):
        self.objectJsonPath.set(jpath)
        tree = self.findWidget('objectTable')
        allFields = [ x[0] for x in self.listColumns ]

        self.fieldMgr = FieldManager(obj, allFields, self.useIncludeButton)
        self.updateFieldEntries(tree, self.fieldMgr)
        
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
            self.listJsonPath.set(selector.jsonPath.replace('%s', '*'))
        else:
            self.listJsonPath.set('$.')

    def onListRun(self):
        args = re.findall('\[(.*?)\]', self.listJsonPath.get())
        v = self.app.getList(self.selectedCollection, args)
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

    def onEntrySelected(self, event):
        log.info(f'Entry selected in {event.widget}')
        tree = event.widget
        if tree.identify_region(event.x, event.y) == 'cell':
            rows = tree.selection()
            if len(rows) == 1:
                values = tree.item(rows[0])['values']
                c1 = tree.column('#1', option='id')
                c2 = tree.column('#2', option='id')
                arg = f'?@.{c1} == "{values[0]}" && @.{c2} == "{values[1]}"'
                args = re.findall('\[(.*?)\]', self.listJsonPath.get())
                args[-1] = arg
                log.info(f' selector args: {args}')
                v = self.app.getList(self.selectedCollection, args)
                if len(v) == 1:
                    selector = self.app.findSelector(self.selectedCollection)
                    log.info(f'  args={args}')
                    expr = selector.jsonPath % tuple(args)
                    self.objectKey = tree.index(rows[0])
                    log.info(f'Object found at {expr} key={self.objectKey}')
                    self.updateObject(expr, v[0])
                else:
                    log.warning(f'Cannot get a unique object in the list')

    def onObjectTableEdit(self, event):
        tree = event.widget
        col = tree.identify_column(event.x)
        row = tree.identify_row(event.y)
        if row is None or col is None:
            return

        cell = tree.selection()[0]
        
    def onListSave(self):
        log.info(f'Save list')

    def onObjectSave(self):
        log.info(f'Save object')
        if self.objectKey is None:
            # New object
            pass
        else:
            # Existing object
            pass
