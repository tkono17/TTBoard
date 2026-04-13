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
        ivdata = self.vmodel.itemView
        ivdata.updateRows()
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
        self.app.selectItem()
        self.itemViewMgr.update(self.app.model.itemData)
        self.updateObject()
        
    def onListSave(self):
        log.info(f'Save list')

    def onFieldChanged(self, *args):
        log.info(f'Field changed')
        self.vmodel.itemView.setState('Modified')
        
    def onShowChildList(self, key, event):
        log.info(f'Show child list e={event}')
        lvdata = self.vmodel.listView
        ivdata = self.vmodel.itemView
        var = ivdata.item[key]
        log.info(f'epath = {ivdata.elementPath}, {ivdata.elementPath.get()}')
        jpath = f'{ivdata.elementPath.get()}.{key}[*]'
        log.info(f'path={jpath}')
        self.app.getListFromPath(jpath, type(var))
        self.listViewMgr.update(self.app.model.listData)
        self.updateListTable()

    def onShowChildObject(self, key, event):
        ivdata = self.vmodel.itemView
        var = ivdata.item[key]
        log.info(f'epath = {ivdata.elementPath}, {ivdata.elementPath.get()}')
        jpath = f'{ivdata.elementPath.get()}.{key}'
        self.app.getObjectFromPath(jpath, type(var))
        self.itemViewMgr.update(self.app.model.itemData)
        self.updateObject()
        
    def onSaveFields(self, event):
        ivdata = self.vmodel.itemView
        idata = self.app.model.itemData
        modified = False

        log.info(f'Save object state={ivdata.state}')

        if ivdata.state in ('New', 'Modified'):
            if idata.isItemScalar():        
                value = ivdata.rows[0].getValue()
                self.app.setValue(value)
            else:
                for row in ivdata.rows:
                    self.app.setField(row.name, row.getValue())
            self.app.saveItem()
            ivdata.setState('Set')
            modified = True

        if modified:
            self.app.save()
