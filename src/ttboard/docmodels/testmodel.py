from dataclasses import dataclass, field
from typing import Optional
from ..tools import JsonSelector
from ..model import Metadata

@dataclass
class TestObject:
    name: Optional[str] = None
    value: Optional[int] = None
    values: list[float] | None = None

@dataclass
class DocumentTest:
    metadata: Metadata
    idata: Optional[int] = None
    fdata: Optional[float] = None
    sdata: Optional[str] = None
    ildata: list[int] = field(default_factory=list)
    sldata: list[str] = field(default_factory=list)
    oldata: list[TestObject] = field(default_factory=list)

def getDocumentClass():
    return DocumentTest

def getAllSelectors():
    selectors = [
        JsonSelector('ildata', int, r'$.ildata[%s]'),
        JsonSelector('sldata', str, r'$.sldata[%s]')
        JsonSelector('oldata', TestObject, r'$.oldata[%s]')
    ]
    return selectors