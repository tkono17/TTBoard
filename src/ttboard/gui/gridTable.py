import tkinter as tk
from tkinter import ttk

class GridTable(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.ncolumns = 1
        self.rows = []

    def trimColumns(self, row, ncols):
        ncols_current = len(row)
        if ncols_current > ncols:
            self.delete(*row[ncols:])
            row = row[0:ncols]
        elif ncols_current < ncols:
            for i in range(ncols - ncols_current):
                row.append(None)

    def setColumns(self, row, columns):
        self.trimColumns(row, len(columns))
        for i, column in enumerate(columns):
            nheadings = len(column)
            row[i] = tk.Entry(self)
            row[i].insert(0, column)
        
    def setHeadings(self, headings):
        if len(self.rows) == 0:
            self.rows.append([])
        self.setColumns(self.rows[0], headings)
        for row in self.rows[0]:
            row.config(state='readonly')

    def insertRow(self, columns):
        self.rows.append([])
        self.setColumns(self.rows[-1], columns)
        
    def deleteRow(self, irow):
        if irow > 0 and irow < len(self.rows):
            for cell in self.rows[irow]:
                cell.destroy()
            self.rows = self.rows[0:irow] + self.rows[irow:]
        pass

    def clear(self):
        for row in self.rows:
            for cell in row:
                cell.destroy()
        self.rows = []
                
    def build(self, vc):
        for irow, row in enumerate(self.rows):
            for icol, cell in enumerate(row):
                if cell is not None:
                    cell.grid(row=irow, column=icol)
        pass
    
    
