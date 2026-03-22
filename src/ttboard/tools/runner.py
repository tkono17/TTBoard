import os
from dataclasses import dataclass, field
from typing import Optional, Any
import logging

log = logging.getLogger(__name__)

@dataclass
class Command:
    line: str
    name: str | None = None
    args: list[int|float|str] = field(default_factory=list)

    def set(self, line: str):
        self.line = line
        
    def decode(self):
        self.name = None
        self.args = []
        
        words = self.line.split()
        self.name = words[0]
        for word in words[1:]:
            arg = self.readArg(word)
            self.args.append(arg)

    def readArg(self, word):
        value = None
        try:
            value = int(word)
        except ValueError as e:
            pass
        if value is None:
            try:
                value = float(word)
            except ValueError as e:
                pass
        if value is None:
            value = word
        return value

    def isValid(self):
        return self.name is not None

    def run(self, app):
        if hasattr(app, self.name):
            func = getattr(app, self.name)
            if func is not None:
                log.info(f'  Running command {self.name}')
                func(*self.args)
        else:
            log.warning(f'  The application does not have a command {self.name}')
            
class AppRunner:
    def __init__(self, app):
        self.app = app
        self.macroPath = None
        self.commands = []
        
    def run(self, macroFile: str):
        self.macroPath = macroFile
        self.commands = self.openMacro()

        for cmd in self.commands:
            cmd.run(self.app)

    def openMacro(self):
        self.commands = []
        if os.path.exists(self.macroPath):
            with open(self.macroPath, 'r') as fin:
                for line in fin.readlines():
                    if len(line)==0 or line[0]=='#': continue
                    if line[-1] == os.linesep: line = line[:-1]
                    line = line.strip()
                    if len(line)>0:
                        cmd = Command(line)
                        cmd.decode()
                        if cmd.isValid(): self.commands.append(cmd)
        return self.commands
    
