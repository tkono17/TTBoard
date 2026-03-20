import os, sys
import json
import jsonpath
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
        self.listElementType = None
        self.listMatches = None
        
        self.currentObject = None
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

    def findall(self, expr):
        return jsonpath.findall(expr, self.model.document)
    
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
        if dn == '': dn = '.'
        if self.model.document is not None and os.path.exists(dn):
            with open(fpath, 'w', encoding='utf8') as fout:
                json.dump(self.model.document, fout, indent=2, ensure_ascii=False)
        else:
            log.warning(f'Try to save document to a JSON file {fpath}')
            dnull = self.model.document is None
            log.warning(f'    Output directory = {dn}, document null? {dnull}')
        pass

    def getList(self, selectorName, args):
        selectors1 = filter(lambda x: x.name == selectorName, self.selectors)
        selectors1 = list(selectors1)
        selector = selectors1[0] if len(selectors1)>0 else None
        
        nargs = selector.jsonPath.count(r'[%s]')
        if (args is None and nargs == 0) or (args is not None and len(args) == nargs):
            v = selector.query(self.model.document, *args)
            self.listMatches = [ x for x in v ]
            self.currentList = selector.findall(self.model.document, *args)
            self.listElementType = selector.elementType
        else:
            self.currentList = None
            self.listElementType = None
            self.listMatches = None
        return self.currentList

    def findSelector(self, sname):
        selector = None
        v = list(filter(lambda x: x.name == sname, self.selectors))
        if len(v) == 1:
            selector = v[0]
        return selector

    def setFieldValue(self, jpath, value):
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
            
