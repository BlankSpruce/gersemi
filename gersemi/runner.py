from dataclasses import astuple
from functools import partial
from itertools import chain
from pathlib import Path
import sys
from typing import Callable
from lark.exceptions import VisitError as LarkVisitError
from gersemi.custom_command_definition_finder import find_custom_command_definitions
from gersemi.exceptions import ASTMismatch, ParsingError
from gersemi.formatter import create_formatter, Formatter
from gersemi.parser import create_parser, create_parser_with_postprocessing
from gersemi.return_codes import SUCCESS, INTERNAL_ERROR
from gersemi.task_result import TaskResult
from gersemi.tasks.check_formatting import check_formatting
from gersemi.tasks.forward_to_stdout import forward_to_stdout
from gersemi.tasks.format_file import format_file, Error, FormattedFile, Result
from gersemi.tasks.rewrite_in_place import rewrite_in_place
from gersemi.tasks.show_diff import show_diff
from gersemi.utils import fromfile, smart_open


print_to_stdout = partial(print, file=sys.stdout, end="")
print_to_stderr = partial(print, file=sys.stderr)


def get_files(paths):
    def get_files_from_single_path(path):
        if path.is_dir():
            return chain(path.rglob("CMakeLists.txt"), path.rglob("*.cmake"),)
        return [path]

    for path in paths:
        for item in get_files_from_single_path(path):
            yield item


def has_custom_command_definition(code):
    lowercased = code.lower()
    has_function_definition = "function" in lowercased and "endfunction" in lowercased
    has_macro_definition = "macro" in lowercased and "endmacro" in lowercased
    return has_function_definition or has_macro_definition


def safe_read(filepath, *args, **kwargs):
    try:
        with smart_open(filepath, "r", *args, **kwargs) as f:
            return f.read()
    except UnicodeDecodeError as exception:
        print_to_stderr(f"File {fromfile(filepath)} can't be read: ", exception)
        return None


def find_all_custom_command_definitions(bare_parser, paths):
    parser = create_parser_with_postprocessing(bare_parser)
    result = dict()
    for filepath in get_files(paths):
        code = safe_read(filepath)
        if code is None or not has_custom_command_definition(code):
            continue

        try:
            parse_tree = parser.parse(code)
            result.update(find_custom_command_definitions(parse_tree))
        except ParsingError as exception:
            print_to_stderr(f"{fromfile(filepath)}{exception}")
        except LarkVisitError as exception:
            print_to_stderr(
                f"Runtime error when interpretting {fromfile(filepath)}: ", exception,
            )
    return result


def select_task(args):
    if args.show_diff:
        return show_diff
    if args.check_formatting:
        return check_formatting
    if args.in_place:
        return rewrite_in_place
    return forward_to_stdout


class LazyFormatter:  # pylint: disable=too-few-public-methods
    def __init__(self, args):
        self.args = args
        self.bare_parser = None
        self.formatter = None

    def _actual_format(self, code):
        return self.formatter.format(code)

    def format(self, code):
        if self.formatter is None:
            self.bare_parser = create_parser()
            self.formatter = create_formatter(
                self.bare_parser,
                self.args.format_safely,
                self.args.line_length,
                find_all_custom_command_definitions(
                    self.bare_parser, self.args.definitions
                ),
            )

        return self._actual_format(code)


ERROR_MESSAGE_TEMPLATES = {
    UnicodeDecodeError: "File {path} can't be read: {exception}",
    ParsingError: "{path}{exception}",
    ASTMismatch: "Failed to format {path}: AST mismatch after formatting",
}
FALLBACK_ERROR_MESSAGE_TEMPLATE = "Runtime error when formatting {path}: {exception}"


def get_error_message(error: Error) -> str:
    exception, path = astuple(error)
    message = FALLBACK_ERROR_MESSAGE_TEMPLATE
    for exception_type, template in ERROR_MESSAGE_TEMPLATES.items():
        if isinstance(exception, exception_type):
            message = template
            break
    return message.format(path=path, exception=exception)


def apply(
    executor: Callable[[FormattedFile], TaskResult], formatted_file: Result
) -> TaskResult:
    if isinstance(formatted_file, Error):
        return TaskResult(
            return_code=INTERNAL_ERROR, to_stderr=get_error_message(formatted_file)
        )

    return executor(formatted_file)


def run_task(
    path: Path, formatter: Formatter, task: Callable[[FormattedFile], TaskResult]
) -> TaskResult:
    formatted_file = format_file(path, formatter)
    return apply(task, formatted_file)


def consume_task_result(task_result: TaskResult) -> int:
    return_code, to_stdout, to_stderr = astuple(task_result)
    if to_stdout != "":
        print_to_stdout(to_stdout)
    if to_stderr != "":
        print_to_stderr(to_stderr)
    return return_code


def run(args):
    formatter = LazyFormatter(args)
    task = select_task(args)
    execute = partial(run_task, formatter=formatter, task=task)
    results = map(execute, get_files(args.sources))
    return max(map(consume_task_result, results), default=SUCCESS)
