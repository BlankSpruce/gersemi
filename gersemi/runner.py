import argparse
from collections import defaultdict
from functools import partial
from itertools import chain
import multiprocessing as mp
import multiprocessing.dummy as mp_dummy
from pathlib import Path
import sys
from typing import Callable, Dict, List, Iterable, Tuple, Union
from gersemi.cache import create_cache
from gersemi.configuration import (
    Configuration,
    ControlConfiguration,
    find_closest_dot_gersemirc,
    make_control_configuration,
    make_outcome_configuration,
    MaxWorkers,
    max_number_of_workers,
    NotSupportedKeys,
    Workers,
)
from gersemi.custom_command_definition_finder import (
    find_custom_command_definitions,
    get_just_definitions,
)
from gersemi.formatted_file import FormattedFile
from gersemi.formatter import create_formatter, NullFormatter, Formatter
from gersemi.mode import get_mode, Mode
from gersemi.parser import PARSER as parser
from gersemi.result import Result, Error, apply, get_error_message
from gersemi.return_codes import SUCCESS, INTERNAL_ERROR
from gersemi.task_result import TaskResult
from gersemi.tasks.check_formatting import check_formatting
from gersemi.tasks.do_nothing import do_nothing
from gersemi.tasks.forward_to_stdout import forward_to_stdout
from gersemi.tasks.format_file import format_file
from gersemi.tasks.rewrite_in_place import rewrite_in_place
from gersemi.tasks.show_diff import show_colorized_diff, show_diff
from gersemi.utils import fromfile, smart_open
from gersemi.keywords import Keywords
from gersemi.warnings import UnknownCommandWarning


CHUNKSIZE = 16


print_to_stdout = partial(print, file=sys.stdout, end="")
print_to_stderr = partial(print, file=sys.stderr)


def get_files(paths: Iterable[Path]) -> Iterable[Path]:
    def get_files_from_single_path(path):
        if path.is_dir():
            return chain(path.rglob("CMakeLists.txt"), path.rglob("*.cmake"))
        return [path]

    return sorted(
        set(
            item.resolve(True) if item != Path("-") else item
            for path in paths
            for item in get_files_from_single_path(path)
        )
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
        return {}

    parse_tree = parser.parse(code)
    return find_custom_command_definitions(parse_tree, filepath)


def find_custom_command_definitions_in_file(
    filepath: Path,
) -> Result[Dict[str, Keywords]]:
    return apply(find_custom_command_definitions_in_file_impl, filepath)


def check_conflicting_definitions(definitions):
    for name, info in definitions.items():
        if len(info) > 1:
            print_to_stderr(f"Warning: conflicting definitions for '{name}':")
            places = sorted(where for _, where in info)
            for index, where in enumerate(places):
                kind = "(used)   " if index == 0 else "(ignored)"
                print_to_stderr(f"{kind} {where}")


def find_all_custom_command_definitions(
    paths: Iterable[Path], pool, quiet: bool
) -> Dict[str, Keywords]:
    result: Dict = {}

    try:
        files = get_files(paths)
    except FileNotFoundError as e:
        # pylint: disable=broad-exception-raised
        raise Exception(f"Definition path doesn't exist: {e.filename}") from e

    find = find_custom_command_definitions_in_file

    for defs in pool.imap_unordered(find, files, chunksize=CHUNKSIZE):
        if isinstance(defs, Error):
            print_to_stderr(get_error_message(defs))
            continue

        for name, info in defs.items():
            if name in result:
                result[name].extend(info)
            else:
                result[name] = info

    if not quiet:
        check_conflicting_definitions(result)

    return get_just_definitions(result)


def select_task(mode: Mode, configuration: Configuration):
    return {
        Mode.ForwardToStdout: lambda _: forward_to_stdout,
        Mode.RewriteInPlace: lambda _: rewrite_in_place,
        Mode.CheckFormatting: lambda _: check_formatting,
        Mode.ShowDiff: lambda config: (
            show_colorized_diff if config.control.color else show_diff
        ),
    }[mode](configuration)


def run_task(
    path: Path,
    formatter: Union[NullFormatter, Formatter],
    task: Callable[[FormattedFile], TaskResult],
) -> TaskResult:
    formatted_file: Result[FormattedFile] = apply(format_file, path, formatter)
    if isinstance(formatted_file, Error):
        return TaskResult(
            path=path,
            return_code=INTERNAL_ERROR,
            to_stderr=get_error_message(formatted_file),
        )
    return task(formatted_file)


def consume_task_result(
    task_result: TaskResult, configuration: Configuration
) -> Tuple[Path, int, bool]:
    if task_result.to_stdout != "":
        print_to_stdout(task_result.to_stdout)

    warnings = (
        [w for w in task_result.warnings if not isinstance(w, UnknownCommandWarning)]
        if not configuration.outcome.warn_about_unknown_commands
        else task_result.warnings
    )

    if not configuration.control.quiet:
        for warning in warnings:
            print_to_stderr(warning.get_message(fromfile(task_result.path)))

        if task_result.to_stderr != "":
            print_to_stderr(task_result.to_stderr)

    return task_result.path, task_result.return_code, (len(warnings) > 0)


def create_pool(is_stdin_in_sources, workers: Workers):
    if is_stdin_in_sources:
        return mp_dummy.Pool

    if isinstance(workers, MaxWorkers):
        value = max_number_of_workers()
    else:
        if workers <= 1:
            return mp_dummy.Pool

        value = workers

    return partial(mp.Pool, processes=value)


def split_files_by_formatting_state(
    cache, configuration_summary: str, files: Iterable[Path]
):
    known_files = cache.get_files(configuration_summary)
    already_formatted_files = []
    files_to_format = []
    for f in files:
        if f not in known_files:
            files_to_format.append(f)
        else:
            s = f.stat()
            if (s.st_size, s.st_mtime_ns) != known_files[f]:
                files_to_format.append(f)
            else:
                already_formatted_files.append(f)

    return already_formatted_files, files_to_format


def store_files_in_cache(
    mode: Mode, cache, configuration_summary: str, files: Iterable[Path]
) -> None:
    if mode in [Mode.CheckFormatting, Mode.RewriteInPlace]:
        cache.store_files(configuration_summary, files)


def compute_error_code(collection):
    return max(collection, default=SUCCESS)


def select_task_for_already_formatted_files(mode: Mode):
    return {
        Mode.ForwardToStdout: forward_to_stdout,
    }.get(mode, do_nothing)


def handle_already_formatted_files(
    mode: Mode, configuration: Configuration, already_formatted_files: Iterable[Path]
) -> int:
    task = select_task_for_already_formatted_files(mode)
    formatter = NullFormatter()
    execute = partial(run_task, formatter=formatter, task=task)
    results = [
        consume_task_result(result, configuration)
        for result in map(execute, already_formatted_files)
    ]
    return compute_error_code(code for _, code, _ in results)


def handle_files_to_format(
    mode: Mode,
    configuration: Configuration,
    cache,
    pool,
    files_to_format: Iterable[Path],
) -> int:
    custom_command_definitions = find_all_custom_command_definitions(
        set(configuration.outcome.definitions), pool, configuration.control.quiet
    )
    formatter = create_formatter(
        not configuration.outcome.unsafe,
        configuration.outcome.line_length,
        configuration.outcome.indent,
        custom_command_definitions,
        configuration.outcome.list_expansion,
    )
    task = select_task(mode, configuration)
    execute = partial(run_task, formatter=formatter, task=task)

    results = [
        consume_task_result(result, configuration)
        for result in pool.imap_unordered(execute, files_to_format, chunksize=CHUNKSIZE)
    ]
    store_files_in_cache(
        mode,
        cache,
        configuration.outcome.summary(),
        (
            path
            for path, code, has_warnings in results
            if code == SUCCESS and path != Path("-") and (not has_warnings)
        ),
    )
    return compute_error_code(code for _, code, _ in results)


class ConfigurationHelper:
    def __init__(self, args: argparse.Namespace, control: ControlConfiguration):
        self.args = args
        self.control = control
        self.processed_configuration_files: List[Path] = []

    def _warn(self, item: NotSupportedKeys, text: str):
        if not self.control.quiet:
            print_to_stderr(f"{item.path}:", text)

    def _inform_about_not_supported_keys(self, item: NotSupportedKeys):
        if item.path in self.processed_configuration_files:
            return

        if item.path is None:
            return

        self.processed_configuration_files.append(item.path)

        if len(item.command_line_only) > 0:
            keys = ", ".join(sorted(item.command_line_only))
            self._warn(
                item, f"these options are supported only through command line: {keys}"
            )

        if len(item.unknown) > 0:
            keys = ", ".join(sorted(item.unknown))
            self._warn(item, f"these options are not supported: {keys}")

    def __call__(self, path: Path) -> Configuration:
        outcome_configuration, not_supported_keys = make_outcome_configuration(
            configuration_file=find_closest_dot_gersemirc(path),
            args=self.args,
        )
        self._inform_about_not_supported_keys(not_supported_keys)
        return Configuration(control=self.control, outcome=outcome_configuration)


def split_files_by_configuration(
    paths: Iterable[Path], args: argparse.Namespace, control: ControlConfiguration
):
    helper = ConfigurationHelper(args, control)
    if control.configuration_file is not None:
        return {helper(control.configuration_file): paths}

    result = defaultdict(list)
    for path in paths:
        result[helper(path)].append(path)

    return result


def run(args: argparse.Namespace):
    try:
        requested_files = get_files(args.sources)
    except FileNotFoundError as e:
        # pylint: disable=broad-exception-raised
        raise Exception(f"Source path doesn't exist: {e.filename}") from e

    mode = get_mode(args)
    control = make_control_configuration(args)
    pool_cm = create_pool(
        is_stdin_in_sources=(Path("-") in requested_files),
        workers=control.workers,
    )
    with create_cache(control.cache) as cache, pool_cm() as pool:
        error_code = SUCCESS
        configuration_buckets = split_files_by_configuration(
            requested_files, args, control
        )

        for config, files in configuration_buckets.items():
            if config.outcome.disable_formatting:
                continue

            already_formatted_files, files_to_format = split_files_by_formatting_state(
                cache, config.outcome.summary(), files
            )

            error_code = compute_error_code(
                [
                    error_code,
                    handle_already_formatted_files(
                        mode, config, already_formatted_files
                    ),
                    handle_files_to_format(mode, config, cache, pool, files_to_format),
                ]
            )

        return error_code
