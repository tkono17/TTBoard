from typing import Optional, Any
from dataclasses import dataclass, field
import tkinter as tk
import jsonpath

@dataclass
class FieldState:
    name: str | None = None
    isActive: bool = True

@dataclass
class ListViewModel:
    selectorNames: list[str] | None = None
    collection: tk.StringVar | None = field(default_factory=tk.StringVar)
    jsonPath: tk.StringVar = field(default_factory=tk.StringVar)
    jsonMatches: list[jsonpath.JSONPathMatch] | None = None
    entries: int | float | str | list[Any] | dict[str, Any] | None = None
    fieldStates: list[FieldState] | None = None
    entryType: str = None
    displayStyle: str = 'table'

    def isSimpleEntry(self):
        return self.entryType in (int, float, str)
    
@dataclass
class FieldViewModel:
    jsonPath: tk.StringVar = field(default_factory=tk.StringVar)
    fieldStates: list[FieldState] | None = None
    properties: dict[str, str] | None = None
    useIncludeButton: bool = True
    
@dataclass
class ViewModel:
    listView: ListViewModel = field(default_factory=ListViewModel)
    fieldView: FieldViewModel = field(default_factory=FieldViewModel)

