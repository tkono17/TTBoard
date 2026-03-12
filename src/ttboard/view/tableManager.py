import tkinter as tk
from tkinter import filedialog
import logging
import importlib.resources
import io
from PIL import Image, ImageTk

log = logging.getLogger(__name__)

class TableManager:
    def __init__(self, columns, entries,
                 allColumns=None, cls=None,
                 useIncludeButton = False,
                 useDeleteButton = False):
        self.enabledColumns = columns
        self.entries = entries
        self.allColumns = allColumns
        #self.requiredColumns = requiredColumns
        self.useIncludeButton = useIncludeButton
        self.useDeleteButton = useDeleteButton
        self.images = {
            'Plus': self.openAssetImage('Plus.png'),
            'TrashBin': self.openAssetImage('TrashBin.png'),
            'EmptyCheckBox': self.openAssetImage('EmptyCheckBox.png'),
            'CheckBoxChecked': self.openAssetImage('CheckBoxChecked.png'),
        }
        log.info(f'  enabled: {self.enabledColumns}')
        log.info(f'  allcolumnns: {self.allColumns}')
        log.info(f'  N entries: {len(self.entries)}')
        for k, v in self.images.items():
            log.info(f'    image {k} : {v is not None}')
        pass

    def openAssetImage(self, fileName):
        image = None
        shape = (15, 15)
        with importlib.resources.open_binary('ttboard.assets', fileName) as fin:
            image_bytes = fin.read()
            image = Image.open(io.BytesIO(image_bytes))
            image1 = image.resize(shape, Image.Resampling.LANCZOS)
            image = ImageTk.PhotoImage(image1)
        return image

    def orderedColumns(self):
        if self.allColumns is None:
            v = [ x for x in self.enabledColumns ]
        else:
            v = [ x for x in self.allColumns if x in self.enabledColumns ]
        if self.useIncludeButton:
            v.remove('Included')
        return v

    def getEntries(self):
        v = []
        for entry in self.entries:
            v.append(self.valuesForEntry(entry))
        return v
    
    def valuesForEntry(self, entry):
        v = []
        image = None
        if self.useIncludeButton:
            if entry['Included']:
                image = self.images['CheckBoxChecked']
            else:
                image = self.images['EmptyCheckBox']
        elif self.useDeleteButton:
            image = self.images['TrashBin']
        for column in self.orderedColumns():
            if column in entry.keys():
                v.append(entry[column])
            else:
                v.append('')
        return (v, image)
        
