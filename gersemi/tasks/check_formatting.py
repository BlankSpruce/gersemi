from gersemi.formatted_file import FormattedFile
from gersemi.return_codes import FAIL, SUCCESS
from gersemi.task_result import TaskResult
from gersemi.utils import fromfile


def check_formatting(formatted_file: FormattedFile) -> TaskResult:
    if formatted_file.before != formatted_file.after:
        return TaskResult(
            path=formatted_file.path,
            return_code=FAIL,
            to_stderr=f"{fromfile(formatted_file.path)} would be reformatted",
        )
    return TaskResult(path=formatted_file.path, return_code=SUCCESS)


def quiet_check_formatting(formatted_file: FormattedFile) -> TaskResult:
    if formatted_file.before != formatted_file.after:
        return TaskResult(path=formatted_file.path, return_code=FAIL)
    return TaskResult(path=formatted_file.path, return_code=SUCCESS)
