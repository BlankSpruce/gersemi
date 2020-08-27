from dataclasses import astuple
from functools import partial
from itertools import chain
import multiprocessing as mp
import multiprocessing.dummy as mp_dummy
from pathlib import Path
import sys
from typing import Callable, Dict, Iterable
from gersemi.configuration import Configuration
from gersemi.custom_command_definition_finder import find_custom_command_definitions
from gersemi.formatter import create_formatter, Formatter
from gersemi.mode import Mode
from gersemi.parser import PARSER as parser
from gersemi.result import Result, Error, apply, get_error_message
from gersemi.return_codes import SUCCESS, INTERNAL_ERROR
from gersemi.task_result import TaskResult
from gersemi.tasks.check_formatting import check_formatting, quiet_check_formatting
from gersemi.tasks.forward_to_stdout import forward_to_stdout
from gersemi.tasks.format_file import format_file, FormattedFile
from gersemi.tasks.rewrite_in_place import rewrite_in_place
from gersemi.tasks.show_diff import show_colorized_diff, show_diff
from gersemi.utils import smart_open
from gersemi.keywords import Keywords


CHUNKSIZE = 16


print_to_stdout = partial(print, file=sys.stdout, end="")
print_to_stderr = partial(print, file=sys.stderr)


def get_files(paths: Iterable[Path]) -> Iterable[Path]:
    def get_files_from_single_path(path):
        if path.is_dir():
            return chain(path.rglob("CMakeLists.txt"), path.rglob("*.cmake"))
        return [path]

    return set(
        item.resolve() if item != Path("-") else item
        for path in paths
        for item in get_files_from_single_path(path)
    )


def has_custom_command_definition(code: str) -> bool:
    lowercased = code.lower()
    has_function_definition = "function" in lowercased and "endfunction" in lowercased
    has_macro_definition = "macro" in lowercased and "endmacro" in lowercased
    return has_function_definition or has_macro_definition


def find_custom_command_definitions_in_file_impl(filepath: Path) -> Dict[str, Keywords]:
    with smart_open(filepath, "r") as f:
        code = f.read()
    if not has_custom_command_definition(code):
        return dict()

    parse_tree = parser.parse(code)
    return find_custom_command_definitions(parse_tree)


def find_custom_command_definitions_in_file(
    filepath: Path,
) -> Result[Dict[str, Keywords]]:
    return apply(find_custom_command_definitions_in_file_impl, filepath)


def find_all_custom_command_definitions(
    paths: Iterable[Path], pool
) -> Dict[str, Keywords]:
    result = dict()

    files = get_files(paths)
    find = find_custom_command_definitions_in_file

    for defs in pool.imap_unordered(find, files, chunksize=CHUNKSIZE):
        if isinstance(defs, Error):
            print_to_stderr(get_error_message(defs))
        else:
            result.update(defs)
    return result


def select_task(mode: Mode, configuration: Configuration):
    return {
        Mode.ForwardToStdout: lambda _: forward_to_stdout,
        Mode.RewriteInPlace: lambda _: rewrite_in_place,
        Mode.CheckFormatting: lambda config: quiet_check_formatting
        if config.quiet
        else check_formatting,
        Mode.ShowDiff: lambda config: show_colorized_diff
        if config.color
        else show_diff,
    }[mode](configuration)


def run_task(
    path: Path, formatter: Formatter, task: Callable[[FormattedFile], TaskResult]
) -> TaskResult:
    formatted_file: Result[FormattedFile] = apply(format_file, path, formatter)
    if isinstance(formatted_file, Error):
        return TaskResult(
            return_code=INTERNAL_ERROR, to_stderr=get_error_message(formatted_file)
        )
    return task(formatted_file)


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


def run(mode: Mode, configuration: Configuration, sources: Iterable[Path]):
    files_to_format = get_files(sources)
    task = select_task(mode, configuration)

    with create_pool(Path("-") in files_to_format) as pool:
        custom_command_definitions = find_all_custom_command_definitions(
            set(configuration.definitions), pool
        )
        formatter = create_formatter(
            not configuration.unsafe,
            configuration.line_length,
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
