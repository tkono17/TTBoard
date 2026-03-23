from typing import Any
from dataclasses import dataclass
import jsonpath
import logging

log = logging.getLogger(__name__)

@dataclass
class JsonSelector:
    name: str
    elementType: Any
    jsonPath: str
    nArgs: int = 0

    def expr(self, json_path, *args):
        return json_path % args
    
    def query(self, document, *args):
        if self.nArgs == len(args):
            args1 = list(map(lambda x: str(x), args))
            expr = self.expr(self.jsonPath, *args1)
        else:
            return None
        log.info(f'  args = {args}')
        log.info(f'  expr = {expr}')
        x = jsonpath.query(expr, document)
        return x
    
    def findall(self, document, *args):
        if self.nArgs == len(args):
            args1 = list(map(lambda x: str(x), args))
            expr = self.expr(self.jsonPath, *args1)
            log.info(f'    JSONPath expr: {expr} {args1}')
        else:
            return None
        x = jsonpath.findall(expr, document)
        return x
    
    def findone(self, document, *args):
        if self.nArgs == len(args):
            args1 = list(map(lambda x: str(x), args))
            expr = self.expr(self.jsonPath, *args1)
        else:
            return None
        x = jsonpath.findone(expr, document)
        return x
    
    def findParent(self, document, *args):
        parentPath, nargs = self.jsonPath, self.nArgs
        i0 = self.jsonPath.rfind('.')
        if i0 > 0:
            parentPath = self.jsonPath[0:i0]
            nargs = self.nArgs - 1
        if nargs == len(args):
            args1 = list(map(lambda x: str(x), args))
            expr = self.expr(parentPath, *args1)
        else:
            return None
        x = jsonpath.findone(expr, document)
        return x

# Functions to be defined in the module containing the data model
def getDocumentClass() -> Any:
    return None

def getAllSelectors() -> list[JsonSelector]:
    return []

