import os, sys
import re
import json
import jsonpath
import importlib
from dataclasses import fields, asdict
import logging
from ..model import AppModel
from ..tools import mainType, readKeyValue, readScalar
from .managers import ListMgr, createItemMgr, ScalarItemMgr, ListItemMgr, ObjectItemMgr

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
        
        self.model.itemData.elementPath = None
        self.model.itemData.containerPath = None
        self.model.itemData.elementMatch = None
        self.model.itemData.containerMatch = None
        self.model.itemData.key = None
        self.model.itemData.item = None
        self.model.itemData.elementType = None

        self.listMgr = ListMgr(self.model.listData, self.model.document)
        self.itemMgr = None

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
            self.initialize()
        else:
            m = None
        return m

    def openJsonFile(self, fpath):
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf8') as fin:
                self.model.documentPath = fpath
                self.model.document = json.load(fin)
                self.listMgr.document = self.model.document
            self.loadModule()
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

    def newDocument(self):
        module_name = None
        if self.model.dataModule is not None:
            module_name = self.model.dataModule.__name__
        self.model.documentPath = None
        e = self.listMgr.newElement(self.model.documentClass)
        self.model.document = e
        self.model.document['metadata']['dataModule'] = module_name
        self.listMgr.document = e
        log.info(f'New document {self.model.document}')
        pass

    def saveAs(self, fileName: str):
        self.model.documentPath = fileName
        self.save()

    def save(self):
        log.info(f'Save {self.model.document}')
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
        self.model.listData.collection = selectorName
        selector = self.findSelector(selectorName)
        selector.composePath(*args)
        v = self.listMgr.findall(selector)
        log.info(f' v = {v}, entries = {self.listMgr.entries}')
        return v

    def findall(self, jpath):
        entries = jsonpath.findall(jpath, self.model.document)
        return entries
    
    def newItem(self):
        e = self.listMgr.newElement()
        log.info(f'newItem {e}')
        self.model.itemData.item = e
        self.itemMgr = createItemMgr(self.model.itemData, self.model.document)
        self.itemMgr.newItem(self.listMgr)

    def selectItem(self, ientry=None):
        log.info(f'selectItem {self.listMgr.data.entries}')
        if ientry is None:
            return self.newItem()
        elif self.listMgr.data.entries is not None and \
            ientry >= 0 and ientry < len(self.listMgr.data.entries):
            self.model.listData.key = ientry
            self.model.itemData.item = self.model.listData.entries[ientry]
            self.itemMgr = createItemMgr(self.model.itemData, self.model.document)
            self.itemMgr.update(self.listMgr)

    def setField(self, key, value):
        tim = type(self.itemMgr)
        log.info(f'setField {tim}')
        if tim == ObjectItemMgr:
            self.itemMgr.setField(key, value)
            self.itemMgr.save()

    def setValue(self, value: int | float | str):
        log.info(f'setValue')
        tim = type(self.itemMgr)
        if tim == ScalarItemMgr:
            self.itemMgr.setValue(value)
            self.itemMgr.save()

    def saveItem(self):
        log.info(f'saveItem')
        if self.itemMgr is not None:
            self.itemMgr.save()
        else:
            log.warning(f'  Failed to save item since item is not selected')

    def updateItem(self, *args):
        log.info(f'updateItem {args}')
        if len(args)==0:
            log.warning(f'  Item was not given, doing nothing')
        for kv in args:
            k, v = readKeyValue(kv)
            if k is None: continue
            self.setField(k, v)
        self.saveItem()
        self.save()
        
    def deleteItem(self, ientry):
        log.info(f'deleteItem')
        self.listMgr.deleteItem(ientry)
        self.save()

    # Combined methods only for CLI
    def addItem(self, *args):
        log.info(f'addItem {args}')
        if len(args)==0:
            log.warning(f'  Item was not given, doing nothing')
        self.newItem()
        for kv in args:
            k, v = readKeyValue(kv)
            if k is None: continue
            self.setField(k, v)
        self.saveItem()
        self.save()

    def addValue(self, value):
        log.info(f'addItem {value}')
        self.newItem()
        self.setValue(value)
        self.saveItem()
        self.save()

    def showList(self):
        log.info(f'Show list')
        if self.listMgr is not None:
            self.listMgr.show()
        else:
            log.warning(f'ListMgr is none, nothing to show')

    def showItem(self):
        fdata = self.model.itemData
        log.info(f'Item fields {fdata.elementPath}')
        if fdata.item is not None:
            for key, value in fdata.item.items():
                log.info(f'  [{key}] {value}')

    def showExamples(self):
        log.info(f'Examples:')
        log.info(f'* Create a new document of a given model')
        log.info(f'  > loadModule ttboard.testmodel')
        log.info(f'  > newDocument')
        log.info(f'  > saveAs a.json')
        log.info(f'* Add entries to the lists')
        log.info(f'* Modify entries in the lists')

    def findSelector(self, sname):
        selector = None
        v = list(filter(lambda x: x.name == sname, self.model.selectors))
        if len(v) == 1:
            selector = v[0]
        return selector
