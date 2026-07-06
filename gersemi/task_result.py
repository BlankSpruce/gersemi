from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass
class TaskResult:
    path: Path
    return_code: int
    to_stdout: str = ""
    to_stderr: str = ""
    warnings: Sequence[str] = ()
