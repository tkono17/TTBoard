import os
import json
import importlib
import logging
from ..model import AppModel

log = logging.getLogger(__name__)

class App:
    def __init__(self):
        #self.settings = AppSettings()
        self.model = AppModel('TTBoard')
        
        self.dataModule = None
        self.documentClass = None
        self.selectors = []

        self.currentList = None
        self.currentObject = None
        self.listElementType = None
        self.objectType = None
        
    def configure(self, settings=None):
        pass

    def initialize(self):
        self.documentClass = None
        self.selectors = None
        if self.dataModule is not None:
            self.documentClass = self.dataModule.getDocumentClass()
            self.selectors = self.dataModule.getAllSelectors()
        pass

    def loadModule(self, moduleName=None):
        m = None
        if moduleName is None and \
           self.model.document is not None and\
           "metadata" in self.model.document.keys() and\
           "dataModule" in self.model.document["metadata"].keys():
            moduleName = self.model.document["metadata"]["dataModule"]
        if moduleName is not None:
            log.info(f'  load data module {moduleName}')
            m = importlib.import_module(moduleName)
            self.dataModule = m
        else:
            m = None
        return m

    def openJsonFile(self, fpath):
        if os.path.exists(fpath):
            with open(fpath, 'r') as fin:
                self.model.document = json.load(fin)
            self.loadModule()
            self.initialize()
        else:
            log.warning(f'JSON file at {fpath} does not exist')
        pass

    def saveJsonFile(self, fpath):
        dn = os.path.dirname(fpath)
        if self.model.document is not None and os.path.exists(dn):
            with open(fpath, 'w', encoding='utf8') as fout:
                json.dump(self.model.document, fout, indent=2, ensure_ascii=False)
        else:
            log.warning(f'Try to save document to a JSON file {fn}')
            dnull = self.model.document is None
            log.warning(f'    Output directory = {dn}, document null? {dnull}')
        pass

    def getList(self, selectorName, args):
        selectors1 = filter(lambda x: x.name == selectorName, self.selectors)
        selectors1 = list(selectors1)
        selector = selectors1[0] if len(selectors1)>0 else None
        
        nargs = selector.jsonPath.count(r'[%s]')
        if (args is None and nargs == 0) or (args is not None and len(args) == nargs):
            self.currentList = selector.findall(self.model.document, *args)
            self.listElementType = selector.elementType
        else:
            self.currentList = None
            self.listElementType = None
        return self.currentList
            
    def findSelector(self, sname):
        selector = None
        v = list(filter(lambda x: x.name == sname, self.selectors))
        if len(v) == 1:
            selector = v[0]
        return selector
    
    def addList(self, name, data):
        v = map(lambda x: x.name == name, self.selectors)
        selector = v[0] if len(v) >= 1 else None
        x = selector.findParent(self.model.document)
        if x is not None:
            x.append(data)
            
    def addObject(self, name, data):
        v = map(lambda x: x.name == name, self.selectors)
        selector = v[0] if len(v) >= 1 else None
        x = selector.findParent(self.model.document)
        if x is not None:
            x.append(data)
