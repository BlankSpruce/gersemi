from dataclasses import dataclass
from pathlib import Path


@dataclass
class TaskResult:
    path: Path
    return_code: int
    to_stdout: str = ""
    to_stderr: str = ""
