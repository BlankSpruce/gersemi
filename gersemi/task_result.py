from dataclasses import dataclass
from pathlib import Path
from gersemi.warnings import FormatterWarnings


@dataclass
class TaskResult:
    path: Path
    return_code: int
    to_stdout: str = ""
    to_stderr: str = ""
    warnings: FormatterWarnings = tuple()
