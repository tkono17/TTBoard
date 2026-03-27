from dataclasses import dataclass, field, fields
from typing import Optional, Any
import jsonpath
import re
from ..tools import JsonSelector

@dataclass
class ListData:
    collection: str | None = None
    jsonPath: str | None = None
    jsonMatches: list[jsonpath.JSONPathMatch] | None = None
    entries: list[Any] | None = None
    elementType: int | float | str | list[Any] | dict[str,Any] | None = None
    key: int | str | None = None

    def allFields(self):
        if self.elementType in (int, float, str):
            return [ 'Value' ]
        else:
            return list(map(lambda x: x.name, fields(self.elementType)))
        return []
        
    def isListSimple(self):
        return self.elementType in (int, float, str)

    def elementPath(self, ientry=None):
        epath = None
        if self.jsonMatches is not None and len(self.jsonMatches)>0 and \
           ientry is not None:
            epath = self.jsonMatches[ientry].path
        else:
            epath = None
        return epath

    def containerPath(self):
        cpath = None
        if self.jsonMatches is not None and len(self.jsonMatches)>0:
            cpath = self.jsonMatches[0].parent.path
        else:
            re1 = re.compile(r'.*(\[.*?\])$')
            mg = re1.search(self.jsonPath)
            if mg is not None:
                matched = mg.group(1)
                ip = self.jsonPath.rfind(matched)
                if ip > 0:
                    cpath = self.jsonPath[0:ip]
        return cpath

@dataclass
class FieldsData:
    elementPath: str | None = None
    containerPath: str | None = None
    elementKey: int | str | None = None
    elementMatch: list[jsonpath.JSONPathMatch] | None = None
    containerMatch: list[jsonpath.JSONPathMatch] | None = None
    fields: dict[str, Any] | None = None
    elementType: int | float | str | list[Any] | dict[str,Any] | None = None
    
    def isEntrySimple(self):
        return self.elementType in (int, float, str)

    def update(self, ldata: ListData,
               ientry: int | None =None,
               obj: Any = None):
        self.elementPath = ldata.elementPath(ientry)
        self.containerPath = ldata.containerPath()
        self.elementKey = ientry
        self.elementMatch = ldata.jsonMatches[ientry]
        self.containerMatch = ldata.jsonMatches[ientry].parent
        self.fields = obj
        self.elementType = ldata.elementType

    def itemKey(self):
        key1 = self.elementPath.replace(self.containerPath, '')
        key = key1[1:-1]
        if key[0] not in ("'", '"'):
            key = int(key)
        return key
    
@dataclass
class AppModel:
    name: str
    version: Optional[str] = None
    extraModuleNames: list[str] | None = None
    extraModules: list[Any] | None = None
    
    documentPath: Optional[str] = None
    #
    document: Optional[dict[str, Any]] = None
    dataModule: Any | None = None
    documentClass: Any | None = None
    selectors: list[JsonSelector] | None = None
    #
    listData: ListData = field(default_factory=ListData)
    fieldsData: FieldsData = field(default_factory=FieldsData)
    
    
