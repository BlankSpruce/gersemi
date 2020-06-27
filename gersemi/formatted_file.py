from dataclasses import dataclass
from pathlib import Path


@dataclass
class FormattedFile:
    before: str
    after: str
    newlines_style: str
    path: Path
