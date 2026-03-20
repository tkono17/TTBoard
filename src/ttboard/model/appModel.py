from dataclasses import dataclass
from typing import Optional, Any
from ..tools import JsonSelector

@dataclass
class AppModel:
    name: str
    version: Optional[str] = None
    extraModuleNames: list[str] | None = None
    extraModules: list[Any] | None = None
    
    documentPath: Optional[str] = None
    #
    document: Optional[dict[str, Any]] = None
    selectors: list[JsonSelector] | None = None

    
