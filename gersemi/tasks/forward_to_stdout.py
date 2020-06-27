from gersemi.formatted_file import FormattedFile
from gersemi.return_codes import SUCCESS
from gersemi.task_result import TaskResult


def forward_to_stdout(formatted_file: FormattedFile) -> TaskResult:
    return TaskResult(SUCCESS, to_stdout=formatted_file.after)
