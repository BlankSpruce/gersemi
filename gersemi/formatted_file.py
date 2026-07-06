from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass
class FormattedFile:
    before: str
    after: str
    newlines_style: str
    path: Path
    warnings: Sequence[str]
