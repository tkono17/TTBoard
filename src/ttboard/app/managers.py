import re
import jsonpath
from dataclasses import fields, asdict, MISSING
from typing import Any
import logging
from ..model import ItemData, ListData
from ..tools import readScalar

log = logging.getLogger(__name__)

class ListMgr:
    def __init__(self, listData, document):
        self.data = listData
        self.document = document
        self.selector = None

    def addItem(self, item):
        self.data.items.append(item)
        cont = self.container()
        if cont is not None:
            cont.append(item)

    def deleteItem(self, i):
        del self.data.items[i]
        cont = self.container()
        if cont is not None:
            del cont[i]

    #def allFields(self):
    #    if self.elementType in (int, float, str):
    #        return [ 'Value' ]
    #    else:
    #        return list(map(lambda x: x.name, fields(self.elementType)))
    #    return []

    def findall(self, selector):
        self.clear()

        self.selector = selector
        self.data.jsonPath = self.selector.jsonPath
        v = self.selector.query(self.document)
        if v is not None:
            log.info(f'  selector jsonPath={selector.jsonPath}')
            self.data.jsonMatches = [ x for x in v ]
            self.data.entries = self.selector.findall(self.document)
            self.data.elementType = self.selector.elementType
        log.info(f'{len(self.data.entries)} entries')
        return self.data.entries

    def findallFromPath(self, jpath, etype):
        self.clear()

        self.data.jsonPath = jpath
        v = jsonpath.query(jpath, self.document)
        if v is not None:
            self.data.jsonMatches = [ x for x in v ]
            self.data.entries = jsonpath.findall(jpath, self.document)
            self.data.elementType = None
        log.info(f'{len(self.data.entries)} entries')
        return self.data.entries

    def show(self):
        n = len(self.data.entries)
        log.info(f'List of {self.data.collection} (x{n})')
        for i, entry in enumerate(self.data.entries):
            log.info(f'  [{i}] {entry}')
        
    def isElementScalar(self):
        return self.elementType in (int, float, str)

    def elementPath(self, ientry=None):
        epath = None
        if self.data.jsonMatches is not None and len(self.data.jsonMatches)>0 and \
           ientry is not None:
            epath = self.data.jsonMatches[ientry].path
        else:
            epath = None
        return epath

    def containerPath(self):
        cpath = None
        if self.data.jsonMatches is not None and len(self.data.jsonMatches)>0:
            cpath = self.data.jsonMatches[0].parent.path
        else:
            re1 = re.compile(r'.*(\[.*?\])$')
            mg = re1.search(self.data.jsonPath)
            if mg is not None:
                matched = mg.group(1)
                ip = self.data.jsonPath.rfind(matched)
                if ip > 0:
                    cpath = self.data.jsonPath[0:ip]
        return cpath
    
    def container(self):
        cont = None
        cpath = self.containerPath()
        matches = jsonpath.query(cpath, self.document)
        if len(matches)==0:
            log.warning(f'Container match {cpath} was not found')
        elif len(matches)==1:
            cmatch = matches[0]
            cpointer = cmatch.pointer()
            cont = cpointer.resolve(self.document)
        return cont

    def newElement(self, elementType=None):
        e = None
        log.info(f'create new element of {elementType}')
        if elementType is None:
            e = self.newElement(self.data.elementType)
        elif elementType in (int, float, str):
            e = elementType()
        elif hasattr(elementType, '__dataclass_fields__'):
            args = []
            for f in fields(elementType):
                if f.default is not MISSING or f.default_factory is not MISSING:
                    log.info(f'  {f} has default')
                    continue
                elif f.type in (int, float, str):
                    args.append(f.type())
                else:
                    e1 = self.newElement(f.type)
                    args.append(e1)
            log.info(f'Element {elementType} with args={args}')
            e = elementType(*args)
            e = asdict(e)
        else:
            e = elementType()
            log.info(f'{elementType}, {e}')
            e = asdict(e)
        return e

    def clear(self):
        self.data.jsonPath = None
        self.data.jsonMatches = None
        self.data.entries = None
        self.data.elementType = None
        self.data.key = None

class ItemMgr:
    def __init__(self, itemData, document):
        self.data = itemData
        self.document = document

    def setElementMatch(self, ematch):
        self.data.elementPath = ematch.path
        self.data.containerPath = ematch.parent.path
        self.data.elementMatch = ematch
        self.data.containerMatch = ematch.parent

    def update(self, listMgr: ListMgr):
        ldata = listMgr.data
        ematch = ldata.jsonMatches[ldata.key] if len(ldata.jsonMatches)>0 else None

        self.data.elementMatch = ematch
        self.data.containerMatch = ematch.parent
        self.data.elementPath = listMgr.elementPath(ldata.key)
        self.data.containerPath = listMgr.containerPath()
        self.data.elementType = listMgr.data.elementType

        log.info(f'  ematch: {ematch}')
        log.info(f'  epath = {self.data.elementPath} T={self.data.elementType}')
        if self.data.elementPath is not None:
            mg = re.match(r'.*\[(.*?)\]$', self.data.elementPath)
            if mg is not None:
                key = readScalar(mg.group(1))
                self.data.elementKey = key
                log.info(f'  Key found in ItemMgr is {key}')
            else:
                log.warning(f'  Failed to parse element path {self.data.elementPath}')
        else:
            log.warning(f'  element path is none')
        self.data.elementMatch = ematch
        pmatches = list(jsonpath.query(self.data.containerPath, self.document))
        self.data.containerMatch = pmatches[0] if len(pmatches)>0 else None
        
    def query(self, selector):
        self.clear()

        self.selector = selector
        self.data.jsonPath = self.selector.jsonPath
        v = self.selector.query(self.document)
        return v
    
    def clear(self):
        self.data.elementPath = None
        self.data.containerPath = None
        self.data.elementKey = None
        self.data.elementMatch = None
        self.data.containerMatch = None
        self.data.item = None
        self.data.elementType = None

    def newItem(self, listMgr: ListMgr):
        self.clear()
        ldata = listMgr.data
        ematch = ldata.jsonMatches[0] if len(ldata.jsonMatches)>0 else None
        self.data.elementPath = listMgr.elementPath()
        self.data.containerPath = listMgr.containerPath()
        self.data.elementKey = None
        self.data.elementMatch = None
        pmatches = list(jsonpath.query(self.data.containerPath, self.document))
        self.data.containerMatch = pmatches[0] if len(pmatches)>0 else None
        self.data.item = listMgr.newElement()
        self.data.elementType = listMgr.data.elementType
    
    def save(self):
        if self.data.elementMatch is not None:
            pointer = self.data.elementMatch.pointer()
            parent, _ = pointer.resolve_parent(self.document)
            log.info(f'save parent= {parent}')
            if type(parent) == list:
                log.info(f'  save item at [{self.data.elementKey}]')
                parent[self.data.elementKey] = self.data.item
            else:
                log.warning(f'  Cannot save item to a non-list container')
        elif self.data.containerMatch is not None:
            pointer = self.data.containerMatch.pointer()
            parent = pointer.resolve(self.document)
            if self.data.elementKey is not None:
                parent[self.data.elementKey] = self.data.item
            elif type(parent) == list:
                parent.append(self.data.item)
                n = len(parent)
                self.data.elementKey = n-1
                epath = self.containerMatch.path + f'[{self.data.elementKey}]'
                matches = jsonpath.query(epath, self.document)
                if len(matches)==0:
                    self.data.elementMatch = matches[0]

class ScalarItemMgr(ItemMgr):
    def __init__(self, itemData, document):
        super().__init__(itemData, document)

    def setValue(self, value: int | float | str):
        self.data.item = value

    def getValue(self):
        return self.data.item
    
class ListItemMgr(ItemMgr):
    def __init__(self, itemData, document):
        super().__init__(itemData, document)

    def setItem(self, i, item):
        self.data.item[i] = item

    def getItem(self, i):
        return self.data.item[i]
    
    def addItem(self, item):
        self.data.item.append(item)

    def deleteItem(self, i):
        del self.data.item[i]

class ObjectItemMgr(ItemMgr):
    def __init__(self, itemData, document):
        super().__init__(itemData, document)

    def setField(self, key: str, value: Any):
        log.info(f'  in setField {self.data}')
        self.data.item[key] = value

    def getField(self, key: str):
        return self.data.item[key]

def createItemMgr(itemData, document):
    mgr = None
    itemType = type(itemData.item)
    if itemType in (int, float, str):
        mgr = ScalarItemMgr(itemData, document)
    elif itemType == list:
        mgr = ListItemMgr(itemData, document)
    elif itemType == dict:
        mgr = ObjectItemMgr(itemData, document)
    else:
        log.warning(f'  Cannot create ItemMgr for {itemData.item}')
    return mgr
