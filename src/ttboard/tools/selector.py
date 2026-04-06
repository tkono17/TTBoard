from typing import Any, Optional
from dataclasses import dataclass
import jsonpath
import re
import logging

log = logging.getLogger(__name__)

@dataclass
class JsonSelector:
    name: str
    elementType: Any
    pathTemplate: str
    jsonPath: Optional[str] = None
    nArgs: int = 0

    def __post_init__(self):
        self.nArgs = 0
        matches = re.findall(r'(\[.*?\])', self.pathTemplate)
        self.nArgs = len(matches)

    def composePath(self, *args):
        self.jsonPath = self.pathTemplate % args
        return self.jsonPath
    
    def query(self, document):
        if self.jsonPath is None:
            log.warning(f'composePath(*args) must be called with arguments before query()')
            return None
        x = jsonpath.query(self.jsonPath, document)
        return x
    
    def findall(self, document):
        if self.jsonPath is None:
            log.warning(f'composePath(*args) must be called with arguments before findall()')
            return None
        x = jsonpath.findall(self.jsonPath, document)
        return x
    
    def findone(self, document, *args):
        if self.jsonPath is None:
            log.warning(f'composePath(*args) must be called with arguments before findone()')
            return None
        x = jsonpath.findone(self.jsonPath, document)
        return x
    
    def findParent(self, document):
        parentPath, nargs = self.jsonPath, self.nArgs
        mg = re.match(r'.*(\[.*?\])', self.jsonPath)
        if mg:
            n = len(mg.group(1))
            parentPath = self.jsonPath[0:-n]
            nargs = self.nArgs - 1
        else:
            return None
        x = jsonpath.findone(parentPath, document)
        return x

# Functions to be defined in the module containing the data model
def getDocumentClass() -> Any:
    return None

def getAllSelectors() -> list[JsonSelector]:
    return []
