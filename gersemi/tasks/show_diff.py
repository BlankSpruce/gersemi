from difflib import unified_diff
from typing import Iterator
from gersemi.formatted_file import FormattedFile
from gersemi.return_codes import SUCCESS
from gersemi.task_result import TaskResult
from gersemi.utils import fromfile, tofile

try:
    from colorama import Fore, Style, init  # type: ignore

    init()

    def colorize(diff):
        for line in diff:
            if line.startswith("+++") or line.startswith("---"):
                yield f"{Style.BRIGHT}{Fore.WHITE}{line}{Style.RESET_ALL}"
            elif line.startswith("@@"):
                yield f"{Fore.CYAN}{line}{Fore.RESET}"
            elif line.startswith("+"):
                yield f"{Fore.GREEN}{line}{Fore.RESET}"
            elif line.startswith("-"):
                yield f"{Fore.RED}{line}{Fore.RESET}"
            else:
                yield line


except ImportError:

    def colorize(diff):
        yield from diff


def get_diff(formatted_file: FormattedFile) -> Iterator[str]:
    return unified_diff(
        a=f"{formatted_file.before}\n".splitlines(keepends=True),
        b=f"{formatted_file.after}\n".splitlines(keepends=True),
        fromfile=fromfile(formatted_file.path),
        tofile=tofile(formatted_file.path),
        n=5,
    )


def show_diff(formatted_file: FormattedFile) -> TaskResult:
    return TaskResult(
        path=formatted_file.path,
        return_code=SUCCESS,
        to_stdout="".join(get_diff(formatted_file)),
    )


def show_colorized_diff(formatted_file: FormattedFile) -> TaskResult:
    return TaskResult(
        path=formatted_file.path,
        return_code=SUCCESS,
        to_stdout="".join(colorize(get_diff(formatted_file))),
    )
