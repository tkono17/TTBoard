import os
from dataclasses import fields, MISSING
import tkinter as tk
from tkinter import filedialog
import jsonpath
import logging
import re
from .tableManager import TableManager, FieldsManager
from .vmodel import ViewModel, FieldState, FieldRow

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
        selectorNames = self.app.selectorNames()
        w = self.findWidget('collectionCBox')
        if w:
            w['values'] = selectorNames
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
        fview = self.vmodel.fieldView
        fview.updateRows()
        log.info(f'  updated fields: {fview.orderedFields()}')
        log.info(f'  updated rows: {fieldMgr.model.rows}')
        table.updateFields(fieldMgr.rows(), self)
        pass
    
    def updateListTable(self):
        lview = self.vmodel.listView
        ldata = self.app.model.listData

        if self.app.isListSimple():
            lview.fieldStates = [ FieldState('Value', True) ]
        else:
            lview.fieldStates = [
                FieldState(f.name, True) for f in fields(ldata.elementType)
                ]
        tree = self.findWidget('listTable')
        columnsEn = [ x.name for x in filter(lambda y: y.isActive, lview.fieldStates)]
        if lview.displayStyle == 'table':
            allColumns = list(map(lambda x: x.name, lview.fieldStates))
            entries = self.app.listEntries()
            if self.app.isListSimple():
                entries = [ { 'Value': x } for x in ldata.entries ]
            log.info(f'Updating simple list in table: {entries}')
            self.listTableMgr = TableManager(columnsEn,
                                             entries,
                                             allColumns=allColumns,
                                             useDeleteButton=True)
            self.updateTableEntries(tree, self.listTableMgr)
        elif lview.displayStyle == 'board':
            self.updateBoardEntries(tree, entries, columnsEn)

    def selectObject(self):
        fdata = self.app.model.fieldsData
        lview = self.vmodel.listView
        fview = self.vmodel.fieldView

        obj = fdata.fields
        keys = obj.keys()
        rows = []
        for fs in lview.fieldStates:
            included, value = False, ''
            vtype = None
            if fs.name in keys:
                included = True
                value = obj[fs.name]
                vtype = type(value)
            frow = FieldRow(included, fs.name,
                            tk.StringVar(value=str(value)),
                            vtype)
            rows.append(frow)
        fview.rows = rows
        log.info(f'  fview = {fview}, rows={fview.rows}')
        
    def updateObject(self):
        fview = self.vmodel.fieldView
        self.fieldMgr = FieldsManager(fview)
        tree = self.findWidget('objectTable')
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
        lview = self.vmodel.listView
        
        lview.collection.set(event.widget.get())
        selector = self.app.findSelector(lview.collection.get())
        if selector:
            lview.jsonPath.set(selector.jsonPath.replace('%s', '*'))
        else:
            lview.jsonPath.set('$.')

    def onListRun(self):
        lview = self.vmodel.listView
        ldata = self.app.model.listData
        
        args = re.findall(r'\[(.*?)\]', lview.jsonPath.get())
        v = self.app.getList(lview.collection.get(), args)
        selector = self.app.findSelector(lview.collection.get())
        if v is None:
            ldata.entries = []
            ldata.jsonMatches = None
        else:
            ldata.entries = v
            ldata.jsonMatches = self.app.listMatches
            log.info(f'  Matches: {ldata.jsonMatches}')
        if selector:
            cls = selector.elementType
            ldata.elementType = cls
            if hasattr(cls, '__dataclass_fields__'):
                lview.fieldStates = [ (x, True) for x 
                                     in cls.__dataclass_fields__.keys()]
            elif cls in (int, float, str):
                lview.fieldStates = [ ('Value', True) ]
            else:
                log.warning(f'Do not know how to handle type {cls}')
        else:
            log.warning(f'No selector for list {lview.collection.get()}')
            lview.fieldStates = []
        self.updateListTable()

    def onEntrySelected(self, event):
        ldata = self.app.model.listData
        fdata = self.app.model.fieldsData
        fview = self.vmodel.fieldView
        
        log.info(f'Entry selected in {event.widget}')
        tree = event.widget
        if tree.identify_region(event.x, event.y) == 'cell':
            rows = tree.selection()
            if len(rows) == 1:
                irow = tree.index(rows[0])
                entry = ldata.entries[irow]
                if self.app.isListSimple():
                    obj = { 'Value': str(entry) }
                else:
                    obj = entry
                fdata.update(ldata, irow, obj)
                if ldata.isListSimple():
                    fview.containerPath.set(fdata.containerPath)
                else:
                    fview.containerPath.set(fdata.elementPath)
                fview.key = irow
                fview.setState('Set')
                self.selectObject()
                self.updateObject()

    def onDeleteEntry(self):
        ldata = self.app.model.listData
    
    def onFieldClicked(self, irow, event):
        log.info(f'Field clicked {event.widget} irow={irow}')
        fview = self.vmodel.fieldView
        fview.rows[irow].isActive = not fview.rows[irow].isActive
        self.updateObject()

    def onNewEntry(self):
        ldata = self.app.model.listData
        fdata = self.app.model.fieldsData
        lview = self.vmodel.listView
        fview = self.vmodel.fieldView
        
        jpath = lview.jsonPath.get()
        log.info(f'Find parent path of {jpath}')
        cpath = None
        obj = None
        if hasattr(ldata.elementType, '__dataclass_fields__'):
            obj = {
                f.name: '' for f in fields(ldata.elementType) \
                if (f.default is MISSING and f.default_factory is MISSING)
            }
            cpath = ldata.containerPath()
        elif ldata.elementType == list:
            obj = { '[]': '[]' }
            cpath = ldata.containerPath()
        else:
            obj = { 'Value': ''}
            cpath = ldata.containerPath()
        fdata.containerPath = cpath
        fdata.jsonMatch = None
        fdata.parentMatch = None
        fdata.fields = obj
        fdata.elementType = ldata.elementType

        fview.containerPath.set(cpath)
        fview.key = None
        ldata.entry = obj
        fview.setState('New')
        self.selectObject()
        self.updateObject()
        
    def onListSave(self):
        log.info(f'Save list')

    def onFieldChanged(self, *args):
        log.info(f'Field changed')
        fview = self.vmodel.fieldView
        fview.setState('Modified')
        
    def onSaveFields(self, event):
        fview = self.vmodel.fieldView
        fdata = self.app.model.fieldsData

        log.info(f'Save object state={fview.state}')
        cpath = fview.containerPath.get()
        modified = False
        cont = None

        if fdata.isEntrySimple():
            cpath = fdata.containerPath
            cmatch = fdata.containerMatch
            if cmatch is None:
                cmatches = jsonpath.query(cpath, self.app.model.document)
                if cmatches is not None and len(cmatches)>0:
                    cmatch = cmatches[0]
                    jpointer = cmatch.pointer()
                    cont = jpointer.resolve(self.app.model.document)
                else:
                    log.warning(f'Cannot identify container of {cpath}')
                    return
            else:
                jpointer = cmatch.pointer()
                cont = jpointer.resolve(self.app.model.document)
            if fview.state == 'New':
                value = fview.rows[0].getValue()
                cont.append(value)
            else:
                log.info(f'Write {cpath} key={fview.key}, cont={cont}')
                cont[fview.key] = fview.rows[0].getValue()
            pass
        else:
            cpath = fdata.elementPath
            cmatch = fdata.elementMatch
            if cmatch is None:
                cpath = fdata.containerPath
                cmatches = jsonpath.query(cpath, self.app.model.document)
                for cmatch in cmatches:
                    jpointer = cmatch.pointer()
                    cont2 = jpointer.resolve(self.app.model.document)
                    cont = {}
                    cont2.append(cont)
                    break
                if cont is None:
                    log.warning(f'Cannot identify container of {cpath}')
                    return
            else:
                jpointer = cmatch.pointer()
                cont = jpointer.resolve(self.app.model.document)
            log.info(f'Got container: {cont}')
            if fview.state == 'New':
                for row in fview.rows:
                    if row.isActive:
                        cont[row.name] = row.value.get()
            else:
                for row in fview.rows:
                    if row.isActive:
                        cont[row.name] = row.value.get()
                    elif row.name in cont.keys():
                        cont.pop(row.name)
            modified = True
        modified = True
        if modified:
            self.app.save()
