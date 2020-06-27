from difflib import unified_diff
from gersemi.formatted_file import FormattedFile
from gersemi.return_codes import SUCCESS
from gersemi.task_result import TaskResult
from gersemi.utils import fromfile, tofile


def show_diff(formatted_file: FormattedFile) -> TaskResult:
    diff = unified_diff(
        a=f"{formatted_file.before}\n".splitlines(keepends=True),
        b=f"{formatted_file.after}\n".splitlines(keepends=True),
        fromfile=fromfile(formatted_file.path),
        tofile=tofile(formatted_file.path),
        n=5,
    )
    return TaskResult(return_code=SUCCESS, to_stdout="".join(diff))
