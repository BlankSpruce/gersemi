from gersemi.formatted_file import FormattedFile
from gersemi.task_result import TaskResult
from gersemi.tasks.check_formatting import check_formatting
from gersemi.tasks.show_diff import get_diff


def check_and_show_diff(
    should_colorize: bool, formatted_file: FormattedFile
) -> TaskResult:
    result = check_formatting(formatted_file)
    result.to_stdout = get_diff(should_colorize, formatted_file)
    return result
