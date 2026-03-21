from dataclasses import dataclass, field, fields
from typing import Optional, Any
import jsonpath
from ..tools import JsonSelector

@dataclass
class ListData:
    collection: str | None = None
    jsonPath: str | None = None
    jsonMatches: list[jsonpath.JSONPathMatch] | None = None
    entries: list[Any] | None = None
    elementType: int | float | str | list[Any] | dict[str,Any] | None = None

    def allFields(self):
        if self.elementType in (int, float, str):
            return [ 'Value' ]
        else:
            return list(map(lambda x: x.name, fields(self.elementType)))
        return []
        
    def isListSimple(self):
        return self.elementType in (int, float, str)
    
    def containerPath(self, ientry=None):
        cpath = None
        if ientry is not None: # List entry selected
            jmatch = self.jsonMatches[ientry]
            containerPath = jmatch.path
            if self.isListSimple():
                containerPath = jmatch.parent.path
        elif self.isListSimple(): # scalar in the list
            jpath = self.jsonPath.get()
            ip = jpath.rfind(r'[')
            if ip > 0:
                containerPath = jpath[0:ip]
        elif len(self.jsonMatches)>0: # New entry
            jpath = self.jsonMatches[0]
            ip = jpath.rfind(r'[')
            if ip > 0:
                containerPath = jpath[0:ip] + '[]'
        else:
            jpath = self.jsonPath.get()
            ip = jpath.rfind(r'[')
            if ip > 0:
                containerPath = jpath[0:ip]              
        return containerPath
    

@dataclass
class FieldsData:
    jsonPath: str | None = None
    jsonMatch: list[jsonpath.JSONPathMatch] | None = None
    parentMatch: list[jsonpath.JSONPathMatch] | None = None
    fields: list[Any] | None = None
    elementType: int | float | str | list[Any] | dict[str,Any] | None = None
    
    def isEntrySimple(self):
        return self.elementType in (int, float, str)
    
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
    
    
