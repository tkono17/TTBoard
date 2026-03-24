import os, sys
import re
import json
import jsonpath
import importlib
from dataclasses import fields
import logging
from ..model import AppModel
from ..tools import mainType, readKeyValue

log = logging.getLogger(__name__)

class App:
    def __init__(self):
        #self.settings = AppSettings()
        self.model = AppModel('TTBoard')
        
        self.model.dataModule = None
        self.model.documentClass = None
        self.model.selectors = []

        self.model.listData.jsonPath = None
        self.model.listData.jsonMatches = None
        self.model.listData.entires = None
        self.model.listData.elementType = None
        
        self.model.fieldsData.elementPath = None
        self.model.fieldsData.containerPath = None
        self.model.fieldsData.elementMatch = None
        self.model.fieldsData.containerMatch = None
        self.model.fieldsData.key = None
        self.model.fieldsData.fields = None
        self.model.fieldsData.elementType = None

    def configure(self, settings=None):
        pass

    def initialize(self):
        self.model.documentClass = None
        self.model.selectors = None
        if self.model.dataModule is not None:
            self.model.documentClass = self.model.dataModule.getDocumentClass()
            self.model.selectors = self.model.dataModule.getAllSelectors()
        pass

    def loadModule(self, moduleName=None):
        m = None
        if moduleName is None and \
           self.model.document is not None and\
           "metadata" in self.model.document.keys() and\
           "dataModule" in self.model.document["metadata"].keys():
            moduleName = self.model.document["metadata"]["dataModule"]
        if moduleName is not None:
            if '' not in sys.path:
                sys.path = [''] + sys.path
            log.info(f'  load data module {moduleName} in {sys.path}')
            m = importlib.import_module(moduleName)
            if m is None and moduleName == 'TestModule':
                dn = Path(__file__).parent.parent.parent
                mpath = dn / 'tests/TestModule'
                log.info(f'TestModule is a special module for test, find it at {mpath}')
                m = importlib.import_module(mpath)
            self.model.dataModule = m
        else:
            m = None
        return m

    def openJsonFile(self, fpath):
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf8') as fin:
                self.model.documentPath = fpath
                self.model.document = json.load(fin)
            self.loadModule()
            self.initialize()
        else:
            log.warning(f'JSON file at {fpath} does not exist')
        pass

    def saveJsonFile(self, fpath):
        dn = os.path.dirname(fpath)
        if dn == '': dn = '.'
        if self.model.document is not None and os.path.exists(dn):
            with open(fpath, 'w', encoding='utf8') as fout:
                json.dump(self.model.document, fout, indent=2, ensure_ascii=False)
        else:
            log.warning(f'Try to save document to a JSON file {fpath}')
            dnull = self.model.document is None
            log.warning(f'    Output directory = {dn}, document null? {dnull}')
        pass

    def save(self):
        fn1 = self.model.documentPath.replace('.json', '-tmp.json')
        fn2 = self.model.documentPath.replace('.json', '-backup.json')
        if os.path.exists(fn1):
            os.remove(fn1)
        self.saveJsonFile(fn1)
        if os.path.exists(fn2):
            os.remove(fn2)
        if os.path.exists(self.model.documentPath):
            os.rename(self.model.documentPath, fn2)
        os.rename(fn1, self.model.documentPath)

    def selectCollection(self, colName):
        self.model.listData.collection = colName
        
    def collectionName(self):
        return self.model.listData.collection
    
    def selectorNames(self):
        return list(map(lambda x: x.name, self.model.selectors))

    def getList(self, selectorName, *args):
        ldata = self.model.listData
        ldata.collection = selectorName
        selector = self.findSelector(selectorName)
        v = selector.query(self.model.document, *args)
        if v is None:
            ldata.jsonPath = None
            ldata.jsonMatches = None
            ldata.entries = None
            ldata.elementType = None
        else:
            ldata.jsonPath = selector.expr(selector.jsonPath, *args)
            ldata.jsonMatches = [ x for x in v ]
            ldata.entries = selector.findall(self.model.document, *args)
            ldata.elementType = selector.elementType
        return ldata.entries

    def findall(self, jpath):
        entries = jsonpath.findall(jpath, self.model.document)
        return entries
    
    def showList(self):
        ldata = self.model.listData
        n = len(ldata.entries)
        log.info(f'List of {ldata.collection} (x{n})')
        for i, entry in enumerate(ldata.entries):
            log.info(f'  [{i}] {entry}')

    def addItem(self, *keyValues):
        log.info(f'addItem {keyValues}')
        ldata = self.model.listData
        fdata = self.model.fieldsData

        obj = {}
        cpath = ldata.jsonPath
        ip = cpath.rfind('[')
        if ip > 0:
            cpath = cpath[0:ip]
        log.info(f'  get container {cpath}')
        matches = list(jsonpath.query(cpath, self.model.document))
        if len(matches)==1:
            cmatch = matches[0]
            pointer = cmatch.pointer()
            cont = pointer.resolve(self.model.document)

            fdata.elementPath = None
            fdata.containerPath = cmatch.path
            fdata.elementKey = None
            fdata.elementMatch = None
            fdata.containerMatch = cmatch
            fdata.elementType = ldata.elementType

        for kv in keyValues:
            k, v = readKeyValue(kv)
            if k is not None:
                obj[k] = v

        if cont is not None:
            log.info(f'  add object to the list (x{len(cont)})')
            cont.append(obj)

            ekey = len(cont) - 1
            epath = cpath + f'[{ekey}]'
            log.info(f'  New item path {epath}')
            matches = list(jsonpath.query(epath, self.model.document))
            fdata.elementPath = epath
            fdata.elementKey = ekey
            if len(matches)==1:
                ematch = matches[0]
                ldata.jsonMatches.append(ematch)
                ldata.entries.append(obj)
                fdata.elementMatch = None
            fdata.fields = obj


    def addValue(self, value):
        log.info(f'addItem {value}')
        ldata = self.model.listData
        fdata = self.model.fieldsData

        value = ldata.elementType(value)

        cpath = ldata.jsonPath
        ip = cpath.rfind('[')
        if ip > 0:
            cpath = cpath[0:ip]
        log.info(f'  get container {cpath}')
        matches = list(jsonpath.query(cpath, self.model.document))
        if len(matches)==1:
            cmatch = matches[0]
            pointer = cmatch.pointer()
            cont = pointer.resolve(self.model.document)

            fdata.elementPath = None
            fdata.containerPath = cmatch.path
            fdata.elementKey = None
            fdata.elementMatch = None
            fdata.containerMatch = cmatch
            fdata.elementType = ldata.elementType

        if cont is not None:
            log.info(f'  add value to the list (x{len(cont)})')
            cont.append(value)

            ekey = len(cont) - 1
            epath = cpath + f'[{ekey}]'
            log.info(f'  New item path {epath}')
            matches = list(jsonpath.query(epath, self.model.document))
            fdata.elementPath = epath
            fdata.elementKey = ekey
            if len(matches)==1:
                ematch = matches[0]
                ldata.jsonMatches.append(ematch)
                ldata.entries.append(value)
                fdata.elementMatch = None
            fdata.fields = { 'Value': value}

    def deleteItem(self, selectorName, *args):
        log.info(f'deleteItem')
        ldata = self.model.listData
        cont, key = None, None

        selector = self.findSelector(selectorName)
        matches = list(selector.query(self.model.document, *args))
        if len(matches)>0:
            match0 = matches[0]
            pointer = match0.pointer()
            cont, _ = pointer.resolve_parent(self.model.document)
            mg = re.search(r'.*\[(.*?)\]$', match0.path)
            if mg:
                key = int(mg.group(1))
            if key >= 0 and key < len(cont):
                del cont[key]
                del ldata.jsonMatches[key]
                del ldata.entries[key]
            else:
                log.warning(f'  key={key} is out-of-range {key>=0} {key<len(cont)}')
        else:
            log.warning(f'  found no matches')

    def getItem(self, selectorName, *args):
        fdata = self.model.fieldsData
        selector = self.findSelector(selectorName)
        v = selector.query(self.model.document, *args)
        if v is None:
            pass
        else:
            v = list(v)
            expr = selector.expr(selector.jsonPath, *args)
            if len(v) == 0:
                log.warning(f'  No item was found for {expr}')
            elif len(v) > 1:
                log.warning(f'  More than one items were found for {expr}')
            else:
                jmatch = v[0]
                entry = selector.findall(self.model.document, *args)[0]
                fdata.elementPath = jmatch.path
                fdata.containerPath = jmatch.parent.path
                fdata.elementKey = None
                fdata.elementMatch = jmatch
                fdata.containerMatch = jmatch.parent
                fdata.elementType = selector.elementType
                if fdata.isEntrySimple():
                    fdata.fields = { 'Value': entry }
                else:
                    fdata.fields = entry
                log.info(f'  fdata={fdata}')
        
    def showItem(self):
        fdata = self.model.fieldsData
        log.info(f'Item fields {fdata.elementPath}')
        for key, value in fdata.fields.items():
            log.info(f'  [{key}] {value}')

    def enableField(self, *fieldNames):
        fdata = self.model.fieldsData
        epath = fdata.elementPath
        if fdata.isEntrySimple():
            log.warning(f'  Cannot enable a field for a simple item')
        else:
            pointer = fdata.elementMatch.pointer()
            obj = pointer.resolve(self.model.document)
            f1 = fields(fdata.elementType)
            names = list(map(lambda x: x.name, f1))
            for fieldName in fieldNames:
                if fieldName in names:
                    if fieldName in obj.keys(): continue
                    f2 = list(filter(lambda x: x.name == fieldName, f1))
                    if len(f2) == 1:
                        ftype = mainType(f2[0])
                        obj[fieldName] = ftype()
                else:
                    log.warning(f'  field {fieldName} is not valid')
                    continue
        self.save()
            
    def disableField(self, *fieldNames):
        fdata = self.model.fieldsData
        epath = fdata.elementPath
        if fdata.isEntrySimple():
            log.warning(f'  Cannot enable a field for a simple item')
        else:
            pointer = fdata.elementMatch.pointer()
            obj = pointer.resolve(self.model.document)
            f1 = fields(fdata.elementType)
            names = list(map(lambda x: x.name, f1))
            for fieldName in fieldNames:
                if fieldName in obj.keys():
                    obj.pop(fieldName)
        self.save()
            
    def findSelector(self, sname):
        selector = None
        v = list(filter(lambda x: x.name == sname, self.model.selectors))
        if len(v) == 1:
            selector = v[0]
        return selector

    def setFieldValue(self, fieldName, value):
        fdata = self.model.fieldsData
        fdata = self.model.fieldsData
        if fdata.isEntrySimple():
            log.warning(f'  Cannot set field value for a simple type')
        else:
            pointer = fdata.elementMatch.pointer()
            obj = pointer.resolve(self.model.document)
            obj[fieldName] = value
        self.save()

    def setItemValue(self, value):
        fdata = self.model.fieldsData
        if fdata.isEntrySimple():
            pointer = fdata.containerMatch.pointer()
            v = pointer.resolve(self.model.document)
            key = fdata.itemKey()
            v[key] = value
        else:
            log.warning(f'  Current item is not of a simple type')
        self.save()

    def setFieldValue1(self, jpath, value):
        matches = jsonpath.query(jpath, self.model.document)
        matches = list(matches)
        match len(matches):
            case 0:
                log.warning(f'  JSONPath {jpath} returned zero matches')
                return None
            case 1:
                pointer = matches[0].pointer()
                parent = pointer.resolve_parent(self.model.document)
                key = str(pointer).split('/')[-1]
                if parent is None or key is None:
                    log.warning(f'  JSONPath {jpath} ->  parent or key is None')
                    return None
                if type(parent) == list:
                    parent[int(key)] = value
                else:
                    parent[key] = value
            case _:
                log.warning(f'  JSONPath {jpath} returned more than 1 matches')
                return None
            
