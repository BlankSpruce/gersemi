from dataclasses import dataclass


@dataclass
class TaskResult:
    return_code: int
    to_stdout: str = ""
    to_stderr: str = ""
