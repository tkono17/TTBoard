import tkinter as tk
from tkinter import filedialog
import logging
from ..tools import openAssetImage

log = logging.getLogger(__name__)

class TableManager:
    def __init__(self, columns, entries, 
                 cls=None,
                 useIncludeButton = False,
                 useDeleteButton = False):
        self.columns = columns
        self.entries = entries
        self.isEntrySimple = False
        
        self.useIncludeButton = useIncludeButton
        self.useDeleteButton = useDeleteButton
        self.images = {
            'Plus': openAssetImage('Plus.png'),
            'TrashBin': openAssetImage('TrashBin.png'),
        }
        log.info(f'  enabled: {self.columns}')
        log.info(f'  N entries: {len(self.entries)}')
        for k, v in self.images.items():
            log.info(f'    image {k} : {v is not None}')
        pass

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
        return (entry, image)
        
class FieldsManager:
    def __init__(self, fieldsViewModel):
        self.model = fieldsViewModel
        #for field in self.model.fields:

    def useIncludButton(self):
        return self.model.useIncludeButton

    def rows(self):
        return self.model.rows
    
