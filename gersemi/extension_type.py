from pathlib import Path
from typing import Union


class ModuleExtension(str):
    @property
    def name(self):
        return str(self)

    @property
    def qualified_name(self):
        return f"gersemi_{self}"


class FileExtension(str):
    def __init__(self, value):
        super().__init__()
        self.path = Path(value).resolve(True)

    @property
    def name(self):
        return str(self.path)

    @property
    def qualified_name(self):
        return self.name


Extension = Union[ModuleExtension, FileExtension]
