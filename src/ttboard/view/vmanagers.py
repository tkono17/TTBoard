from dataclasses import fields
import tkinter as tk
from tkinter import ttk
import logging
from ..model import ListData, ItemData
from .vmodel import ListViewModel, FieldState, FieldValues, ItemViewModel, FieldRow

log = logging.getLogger(__name__)

def isSimpleType(etype):
    if etype in (int, float, str):
        return True
    else:
        return False

def tableCellContent(value):
    x = None
    vtype = type(value)
    if isSimpleType(vtype):
        x = str(value)
    elif vtype == list:
        x = f'list[{len(value)}]'
    else:
        x = f'{...}'
    return x

class ListViewMgr:
    def __init__(self, vmodel: ListViewModel):
        self.lvdata = vmodel

    def updateHeaderRows(self):
        self.lvdata.header = []
        self.lvdata.rows = []
        self.lvdata.header = [ fstate.name for fstate 
                              in filter(lambda x: x.isActive, self.lvdata.fieldStates)]
        #log.info(f'item = {self.lvdata.items}, type={self.lvdata.elementType}')
        if self.lvdata.elementType is not None:
            if isSimpleType(self.lvdata.elementType):
                for item in self.lvdata.items:
                    log.info(f'  set field value {item}')
                    fvalues = FieldValues([item])
                    self.lvdata.rows.append(fvalues)
            elif self.lvdata.elementType == list:
                for item in self.lvdata.items:
                    log.info(f'  set field list {item}')
                    fvalues = FieldValues([tableCellContent(item)])
                    self.lvdata.rows.append(fvalues)
            else:
                for item in self.lvdata.items:
                    values = []
                    keys = item.keys()
                    #log.info(f'  set field item {item}')
                    for k in self.lvdata.header:
                        if k in keys:
                            values.append(tableCellContent(item[k]))
                        else:
                            values.append(None)
                    fvalues = FieldValues(values)
                    self.lvdata.rows.append(fvalues)
        elif len(self.lvdata.items)>0:
            e = self.lvdata.items[0]
            etype = type(e)
            if isSimpleType(etype):
                for item in self.lvdata.items:
                    log.info(f'  no set field value {item}')
                    fvalues = FieldValues([item])
                    self.lvdata.rows.append(fvalues)
            elif etype == list:
                for item in self.lvdata.items:
                    log.info(f'  no set field list {item}')
                    fvalues = FieldValues([tableCellContent(item)])
                    self.lvdata.rows.append(fvalues)
            else:
                for item in self.lvdata.items:
                    values = []
                    keys = item.keys()
                    for k in self.lvdata.header:
                        if k in keys:
                            values.append(tableCellContent(item[k]))
                        else:
                            values.append(None)
                    fvalues = FieldValues(values)
                    self.lvdata.rows.append(fvalues)
        #log.info(f'  List data: {self.lvdata}')
        pass

    def update(self, ldata: ListData):
        self.lvdata.collection = tk.StringVar(value=ldata.collection)
        self.lvdata.jsonPath = tk.StringVar(value=ldata.jsonPath)
        self.lvdata.items = ldata.entries
        self.lvdata.elementType = ldata.elementType
        self.lvdata.fieldStates = []
        self.lvdata.displayStyle = 'table'
        if ldata.elementType is not None:
            if ldata.isListSimple():
                self.lvdata.fieldStates.append(FieldState('Value', True))
            elif ldata.elementType is list:
                self.lvdata.fieldStates.append(FieldState('Value', True))
            else:
                if hasattr(ldata.elementType, '__dataclass_fields__'):
                    fv = fields(ldata.elementType)
                    for f in fv:
                        self.lvdata.fieldStates.append(FieldState(f.name, True))
        else:
            if len(self.lvdata.items)>0:
                e = self.lvdata.items[0]
                etype = e
                if isSimpleType(e):
                    self.lvdata.fieldStates.append(FieldState('Value', True))
                elif etype is list:
                    self.lvdata.fieldStates.append(FieldState('Value', True))
                else:
                    keys = e.keys()
                    self.lvdata.fieldStates = [ FieldState(k, True) for k in keys ]
        self.updateHeaderRows()

class ItemViewMgr:
    def __init__(self, vmodel: ItemViewModel):
        self.ivdata = vmodel

    def update(self, idata: ItemData):
        self.ivdata.elementPath = tk.StringVar(value=idata.elementPath)
        self.ivdata.item = idata.item
        self.ivdata.key = idata.elementKey
        self.ivdata.rows = []
        self.ivdata.state = 'Set' if idata.elementKey is not None else 'New'
        self.ivdata.useIncludeButton = True
        self.ivdata.elementType = idata.elementType
        log.info(f'  ItemViewMgr etype = {self.ivdata.elementType}')

        log.info(f'ItemViewMgr update: {idata}')
        if isSimpleType(idata.elementType):
            var = None
            if idata.elementType == int:
                var = tk.IntVar(value=idata.item)
            elif idata.elementType == float:
                var = tk.FloatVar(value=idata.item)
            elif idata.elementType == str:
                var = tk.StringVar(value=idata.item)
            frow = FieldRow(name='Value', isActive=True, value=var, valueType=idata.elementType)
            self.ivdata.rows.append(frow)
        elif idata.elementType == list:
            n = len(idata.item)
            #var = tk.StringVar(value=f'list[{n}]')
            var = idata.item
            frow = FieldRow(name='Value', isActive=True, value=var, valueType=list)
            self.ivdata.rows.append(frow)
        else:
            for c, value in idata.item.items():
                vtype = type(value)
                if vtype == int:
                    var = tk.IntVar(value=value)
                elif vtype == float:
                    var = tk.FloatVar(value=value)
                elif vtype == str:
                    var = tk.StringVar(value=value)
                else:
                    var = value
                frow = FieldRow(name=c, isActive=True, value=var, valueType=type(value))
                log.info(frow)
                self.ivdata.rows.append(frow) 

