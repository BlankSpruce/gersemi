from typing import List
from gersemi.formatted_file import FormattedFile
from gersemi.return_codes import FAIL, SUCCESS
from gersemi.task_result import TaskResult
from gersemi.warnings import FormatterWarning, WrongFormattingWarning


def check_formatting(formatted_file: FormattedFile) -> TaskResult:
    warnings: List[FormatterWarning] = list(formatted_file.warnings)
    if formatted_file.before != formatted_file.after:
        code = FAIL
        warnings.append(WrongFormattingWarning())
    else:
        code = SUCCESS

    return TaskResult(path=formatted_file.path, return_code=code, warnings=warnings)
