import tkinter as tk
from tkinter import filedialog
import logging
from ..tools import openAssetImage

log = logging.getLogger(__name__)

class TableManager:
    def __init__(self, columns, entries,
                 allColumns=None, cls=None,
                 useIncludeButton = False,
                 useDeleteButton = False):
        self.enabledColumns = columns
        self.entries = entries
        self.allColumns = allColumns

        self.useIncludeButton = useIncludeButton
        self.useDeleteButton = useDeleteButton
        self.images = {
            'Plus': openAssetImage('Plus.png'),
            'TrashBin': openAssetImage('TrashBin.png'),
        }
        log.info(f'  enabled: {self.enabledColumns}')
        log.info(f'  allcolumnns: {self.allColumns}')
        log.info(f'  N entries: {len(self.entries)}')
        for k, v in self.images.items():
            log.info(f'    image {k} : {v is not None}')
        pass

    def orderedColumns(self):
        if self.allColumns is None:
            v = [ x for x in self.enabledColumns ]
        else:
            v = [ x for x in self.allColumns if x in self.enabledColumns ]
        return v

    def getEntries(self):
        v = []
        for entry in self.entries:
            v.append(self.valuesForEntry(entry))
        return v
    
    def valuesForEntry(self, entry):
        v = []
        image = None
        if self.useDeleteButton:
            image = self.images['TrashBin']
        for column in self.orderedColumns():
            if column in entry.keys():
                v.append(entry[column])
            else:
                v.append('')
        return (v, image)
        
class FieldManager:
    def __init__(self, obj, allFields, cls=None,
                 useIncludeButton = False):
        self.obj = obj
        self.allFields = allFields
        self.useIncludeButton = useIncludeButton

    def getFields(self):
        objkeys = self.obj.keys()
        orderedFields = [ (fn, True, self.obj[fn]) for fn in self.allFields\
                          if fn in objkeys]
        orderedFields += [ (fn, False, '') for fn in self.allFields\
                          if fn not in objkeys]
        return orderedFields
