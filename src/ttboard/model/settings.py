from dataclasses import dataclass

class AppSettings:
    name: str
    version: str
    extra_packages: list[str]
    
