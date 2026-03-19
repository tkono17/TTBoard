from dataclasses import dataclass
import ttboard

@dataclass
class Date:
    year: int
    month: int
    day: int
    
@dataclass
class TestData:
    name: str
    dates: list[Date]

@dataclass
class TestDocument:
    metadata: ttboard.Metadata
    objects: list[TestData]

def getAllSelectors():
    selectors = [
        ttboard.JsonSelector('objects', None, '$.objects[%s]', 1),
        ttboard.JsonSelector('dates', None, '$.objects[%s].dates[%s]', 1)
        ]
    return selectors

def getDocumentClass():
    return TestDocument


