import os
from dataclasses import fields, MISSING
import tkinter as tk
from tkinter import filedialog
import jsonpath
import logging
import re
from ..tools import mainType
from .tableManager import TableManager, FieldsManager
from .vmodel import ViewModel, FieldState, FieldRow
from .vmanagers import ListViewMgr, ItemViewMgr, isSimpleType

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

        self.listViewMgr = ListViewMgr(self.vmodel.listView)
        self.itemViewMgr = ItemViewMgr(self.vmodel.itemView)

    def updateListViewModel(self, listData):
        self.vmodel.listView.update(listData)

    def updateItemViewModel(self, itemData):
        self.vmodel.itemView.update(itemData)
        
    def updateListView(self):
        self.updateListTable()

    def updateItemView(self):
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
        selectorNames = self.app.selectorNames()
        w = self.findWidget('collectionCBox')
        if w:
            w['values'] = selectorNames
        else:
            log.warning(f'  Widget collectionCBox was not found')

    def updateTableEntries(self, table, tableMgr):
        if table:
            table.delete(*table.get_children())
            ocolumns = tableMgr.columns
            log.info(f'  ordered columns: {ocolumns}')

            table.config(show='tree headings', columns=ocolumns)
            for heading in ocolumns:
                table.heading(heading, text=heading)
                table.column(heading, stretch=tk.NO)

            table.heading('#0', text='Icon')
            table.column('#0', minwidth=50, width=60, stretch=tk.NO)
            entries = tableMgr.getEntries()
            for fvalues, image in entries:
                values = fvalues.values
                log.info(f'values= {values}')
                if image is not None:
                    table.insert('', 'end', image=image, values=values)
                else:
                    table.insert('', 'end', values=values)
        pass
    
    def updateFieldEntries(self, table, fieldMgr):
        fview = self.vmodel.itemView
        fview.updateRows()
        table.updateFields(fieldMgr.rows(), self)
        pass
    
    def updateListTable(self):
        lvdata = self.vmodel.listView
        tree = self.findWidget('listTable')
        columnsEn = lvdata.header
        if lvdata.displayStyle == 'table':
            self.listTableMgr = TableManager(lvdata.header,
                                             lvdata.rows,
                                             useDeleteButton=True)
            self.updateTableEntries(tree, self.listTableMgr)
        elif lvdata.displayStyle == 'board':
            #self.updateBoardEntries(tree, entries, columnsEn)
            log.warning('Board view not supported yet')
            pass

    def selectObject(self):
        lvdata = self.vmodel.listView
        ivdata = self.vmodel.itemView

        ivdata.elementPath.set(fdata.elementPath)
        log.info(f'Select object at {ivdata.elementPath.get()}')
        keys = obj.keys()
        rows = []
        fieldNames = []
        if isSimpleType(lvdata.elementType):
            valueField = tk.StringVar(ivdata.item)
            self.itemViewMgr.update()
            row = FieldRow(True, 'Value', valueField, str)
            rows.append(row)
        else:
            for field in fields(ldata.elementType):
                included, value = False, ''
                vtype = mainType(field)
                valueField = None
                if field.name in keys:
                    included = True
                    value = obj[field.name]
                    if type(value) in (list, dict):
                        valueField = value
                    else:
                        valueField = tk.StringVar(value=value)
                row = FieldRow(included, field.name, valueField, vtype)
                rows.append(row)
        ivdata.rows = rows
        log.info(f'  ivdata = {ivdata}, rows={ivdata.rows}')
        
    def updateObject(self):
        ivdata = self.vmodel.itemView
        log.info(f'Update object {ivdata}')
        self.fieldMgr = FieldsManager(ivdata)
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
            lview.jsonPath.set(selector.pathTemplate.replace('%s', '*'))
        else:
            lview.jsonPath.set('$.')

    def onListRun(self):
        lview = self.vmodel.listView
        ldata = self.app.model.listData
        
        args = re.findall(r'\[(.*?)\]', lview.jsonPath.get())
        v = self.app.getList(lview.collection.get(), *args)
        self.listViewMgr.update(self.app.model.listData)
        self.updateListTable()

    def onEntrySelected(self, event):
        log.info(f'Entry selected in {event.widget}')
        tree = event.widget
        if tree.identify_region(event.x, event.y) == 'cell':
            rows = tree.selection()
            if len(rows) == 1:
                irow = tree.index(rows[0])
                self.app.selectItem(irow)
                self.itemViewMgr.update(self.app.model.itemData)
                self.updateObject()

    def onDeleteEntry(self):
        ldata = self.app.model.listData
    
    def onFieldClicked(self, irow, event):
        log.info(f'Field clicked {event.widget} irow={irow}')
        ivdata = self.vmodel.itemView
        ivdata.rows[irow].isActive = not ivdata.rows[irow].isActive
        self.updateObject()

    def onNewEntry(self):
        ldata = self.app.model.listData
        fdata = self.app.model.itemData
        lview = self.vmodel.listView
        fview = self.vmodel.itemView
        
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
        fdata.item = obj
        fdata.elementType = ldata.elementType

        fview.elementPath.set(cpath)
        fview.key = None
        ldata.entry = obj
        fview.setState('New')
        self.selectObject()
        self.updateObject()
        
    def onListSave(self):
        log.info(f'Save list')

    def onFieldChanged(self, *args):
        log.info(f'Field changed')
        fview = self.vmodel.itemView
        fview.setState('Modified')
        
    def onSaveFields(self, event):
        fview = self.vmodel.itemView
        fdata = self.app.model.itemData

        log.info(f'Save object state={fview.state}')
        cpath = fview.elementPath.get()
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
                        cont[row.name] = row.getValue()
            else:
                for row in fview.rows:
                    if row.isActive:
                        value = row.getValue()
                        log.info(f'  value of {row.name} is {value}, T={row.valueType}')
                        cont[row.name] = value
                    elif row.name in cont.keys():
                        cont.pop(row.name)
            modified = True
        modified = True
        if modified:
            self.app.save()
