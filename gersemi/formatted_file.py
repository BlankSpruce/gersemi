from dataclasses import dataclass
from pathlib import Path
from gersemi.warnings import FormatterWarnings


@dataclass
class FormattedFile:
    before: str
    after: str
    newlines_style: str
    path: Path
    warnings: FormatterWarnings
