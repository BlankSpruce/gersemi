from gersemi.formatted_file import FormattedFile
from gersemi.return_codes import SUCCESS
from gersemi.task_result import TaskResult
from gersemi.utils import smart_open


def rewrite_in_place(formatted_file: FormattedFile) -> TaskResult:
    if formatted_file.before != formatted_file.after:
        with smart_open(
            formatted_file.path, "w", newline=formatted_file.newlines_style
        ) as f:
            print(formatted_file.after, file=f, end="")
    return TaskResult(path=formatted_file.path, return_code=SUCCESS)
