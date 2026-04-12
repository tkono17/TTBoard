from typing import Optional, Any
from dataclasses import dataclass, field, fields
import tkinter as tk
from tkinter import ttk
import jsonpath
from ..model import ListData, ItemData

@dataclass
class FieldState:
    name: str | None = None
    isActive: bool = True

@dataclass
class FieldValues:
    values: list[int|float|str|None] = field(default_factory=list)

@dataclass
class ListViewModel:
    collection: tk.StringVar | None = field(default_factory=tk.StringVar)
    jsonPath: tk.StringVar = field(default_factory=tk.StringVar)
    items: list[Any] = field(default_factory=list)
    elementType: Any | None = None
    fieldStates: list[FieldState] | None = field(default_factory=list)
    header: list[str] = field(default_factory=list)
    rows: list[FieldValues] = field(default_factory=list)
    displayStyle: str = 'table'

    def isSimpleEntry(self):
        return self.entryType in (int, float, str)

    def activeFields(self):
        fields = filter(lambda x: x.isActive, self.fieldStates)
        return list(map(lambda x: x.name, fields))

@dataclass
class FieldRow:
    isActive: bool = True
    name: str | None = None
    value: tk.StringVar | list[Any] | dict[str,Any] | None = None
    valueType: int | str | float | list | dict | Any | None = None

    def getValue(self):
        value = None
        tvalue = type(self.value)
        if tvalue == tk.StringVar:
            svalue = self.value.get()
            value = self.valueType(svalue)
        elif tvalue in (list, dict):
            value = self.value
        return value
            
@dataclass
class ItemViewModel:
    elementPath: tk.StringVar = field(default_factory=tk.StringVar)
    key: str | int | None = None
    rows: list[FieldRow] | None = field(default_factory=list)
    state: str | None = None
    useIncludeButton: bool = True

    def setState(self, newState):
        if newState == 'Modified' and self.state == 'New':
            pass
        else:
            self.state = newState
            
    def orderedFields(self):
        rows1 = list(filter(lambda x: x.isActive, self.rows))
        rows0 = list(filter(lambda x: not x.isActive, self.rows))
        return rows1 + rows0

    def updateRows(self):
        #rowMap = { row.name: row for row in self.rows }
        #ofields = self.orderedFields()
        #elf.rows = [ rowMap[f.name] for f in ofields ]
        return self.rows
    
@dataclass
class ViewModel:
    listView: ListViewModel = field(default_factory=ListViewModel)
    itemView: ItemViewModel = field(default_factory=ItemViewModel)

