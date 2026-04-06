from dataclasses import dataclass
from typing import Optional

@dataclass
class Metadata:
    name: str
    version: str
    dataModule: str
