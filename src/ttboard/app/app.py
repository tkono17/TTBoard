import os
import json
import importlib
from ..model import AppModel

class App:
    def __init__(self):
        #self.settings = AppSettings()
        self.model = AppModel('TTBoard')

    def configure(self, settings=None):
        pass

    def initialize(self):
        pass

    def loadModule(self, moduleName):
        m = importlib.import_module(moduleName)
        return m
    
    def openJsonFile(self, fpath):
        if os.path.exists(fpath):
            with open(fpath, 'r') as fin:
                self.model.document = json.load(fin)
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
