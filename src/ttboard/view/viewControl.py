import os
import tkinter as tk
from tkinter import filedialog
import logging
import re
from .tableManager import TableManager, FieldManager
from .vmodel import ViewModel

log = logging.getLogger(__name__)


class ViewControl:
    def __init__(self, gui, app):
        self.gui = gui
        self.app = app

        # GUI widgets
        self.widgets = {}

        self.fileTypes = [ ('JSON file', '*.json'), ('', '*') ]
        self.fileDirName = os.getcwd()

        # Data related to panels
        self.vmodel = ViewModel()

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
        ldata = self.vmodel.listView
        
        ldata.selectorNames = list(map(lambda x: x.name, self.app.selectors))
        self.gui.mainPanel.listPanel
        w = self.findWidget('collectionCBox')
        if w:
            w['values'] = ldata.selectorNames
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
        ldata = self.vmodel.listView
        
        tree = self.findWidget('listTable')
        columnsEn = [ x[0] for x in filter(lambda y: y[1], ldata.fieldStates)]
        if ldata.displayStyle == 'table':
            allColumns = list(map(lambda x: x[0], ldata.fieldStates))
            entries = ldata.entries
            if ldata.isSimpleEntry():
                entries = [ { 'Value': x } for x in ldata.entries ]
                log.info(f'Updating simple list in table: {entries}')
            self.listTableMgr = TableManager(columnsEn,
                                             entries,
                                             allColumns=allColumns,
                                             useDeleteButton=True)
            self.updateTableEntries(tree, self.listTableMgr)
        elif ldata.displayStyle == 'board':
            self.updateBoardEntries(tree, entries, columnsEn)

    def updateObject(self, jpath, obj):
        ldata = self.vmodel.listView
        fdata = self.vmodel.fieldView
        
        fdata.jsonPath.set(jpath)
        tree = self.findWidget('objectTable')
        allFields = [ x[0] for x in ldata.fieldStates ]

        self.fieldMgr = FieldManager(obj, allFields, fdata.useIncludeButton)
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
        ldata = self.vmodel.listView
        
        ldata.collection.set(event.widget.get())
        selector = self.app.findSelector(ldata.collection.get())
        if selector:
            ldata.jsonPath.set(selector.jsonPath.replace('%s', '*'))
        else:
            ldata.jsonPath.set('$.')

    def onListRun(self):
        ldata = self.vmodel.listView
        
        args = re.findall(r'\[(.*?)\]', ldata.jsonPath.get())
        v = self.app.getList(ldata.collection.get(), args)
        selector = self.app.findSelector(ldata.collection.get())
        if v is None:
            ldata.entries = []
            ldata.matches = None
        else:
            ldata.entries = v
            ldata.matches = self.app.listMatches
            log.info(f'  Matches: {ldata.matches}')
        if selector:
            cls = selector.elementType
            ldata.entryType = cls
            if hasattr(cls, '__dataclass_fields__'):
                ldata.fieldStates = [ (x, True) for x 
                                     in cls.__dataclass_fields__.keys()]
            elif cls in (int, float, str):
                ldata.fieldStates = [ ('Value', True) ]
            else:
                log.warning(f'Do not know how to handle type {cls}')
        else:
            ldata.fieldStates = []
        self.updateListTable()

    def onEntrySelected(self, event):
        ldata = self.vmodel.listView
        
        log.info(f'Entry selected in {event.widget}')
        tree = event.widget
        if tree.identify_region(event.x, event.y) == 'cell':
            rows = tree.selection()
            if len(rows) == 1:
                irow = tree.index(rows[0])
                jpath = ldata.matches[irow] if len(ldata.matches)>=(irow+1) else ''
                obj = { 'Value': str(obj) } if ldata.isSimpleEntry() \
                    else ldata.entries[irow]
                self.updateObject(jpath.path, obj)

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
        if False:
            # New object
            pass
        else:
            # Existing object
            pass
