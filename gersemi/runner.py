from dataclasses import astuple
from functools import partial
from itertools import chain
import multiprocessing as mp
import multiprocessing.dummy as mp_dummy
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


CHUNKSIZE = 16


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


def find_custom_command_definitions_in_file(filepath, parser):
    code = safe_read(filepath)
    if code is None or not has_custom_command_definition(code):
        return None

    try:
        parse_tree = parser.parse(code)
        return find_custom_command_definitions(parse_tree)
    except ParsingError as exception:
        print_to_stderr(f"{fromfile(filepath)}{exception}")
    except LarkVisitError as exception:
        print_to_stderr(
            f"Runtime error when interpretting {fromfile(filepath)}: ", exception,
        )
    return None


def find_all_custom_command_definitions(bare_parser, paths, pool):
    parser = create_parser_with_postprocessing(bare_parser)
    result = dict()

    files = list(get_files(paths))
    find = partial(find_custom_command_definitions_in_file, parser=parser)

    for defs in pool.imap_unordered(find, files, chunksize=CHUNKSIZE):
        if defs is not None:
            result.update(defs)
    return result


def select_task(args):
    if args.show_diff:
        return show_diff
    if args.check_formatting:
        return check_formatting
    if args.in_place:
        return rewrite_in_place
    return forward_to_stdout


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


def create_pool(is_stdin_in_sources):
    if is_stdin_in_sources:
        return mp_dummy.Pool()
    return mp.Pool(processes=mp.cpu_count())


def run(args):
    bare_parser = create_parser()
    files_to_format = list(get_files(args.sources))
    task = select_task(args)

    with create_pool(Path("-") in files_to_format) as pool:
        custom_command_definitions = find_all_custom_command_definitions(
            bare_parser, args.definitions, pool
        )
        formatter = create_formatter(
            bare_parser,
            args.format_safely,
            args.line_length,
            custom_command_definitions,
        )
        execute = partial(run_task, formatter=formatter, task=task)

        return max(
            map(
                consume_task_result,
                pool.imap_unordered(execute, files_to_format, chunksize=CHUNKSIZE),
            ),
            default=SUCCESS,
        )
