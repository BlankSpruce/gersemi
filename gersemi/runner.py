import argparse
from collections import defaultdict, ChainMap
import collections.abc
from functools import partial
from hashlib import sha1
from itertools import chain
import multiprocessing as mp
import multiprocessing.dummy as mp_dummy
from pathlib import Path
import sys
from typing import Callable, Dict, List, Iterable, Optional, Tuple, Union
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
    OutcomeConfiguration,
    Workers,
)
from gersemi.configuration_reports import minimal_report, verbose_report
from gersemi.custom_command_definition_finder import (
    find_custom_command_definitions,
    get_just_definitions,
)
from gersemi.formatted_file import FormattedFile
from gersemi.formatter import create_formatter, NullFormatter, Formatter
from gersemi.mode import get_mode, Mode
from gersemi.parser import PARSER as parser
from gersemi.extensions import load_definitions_from_extensions
from gersemi.print_config_kind import PrintConfigKind
from gersemi.result import Result, Error, apply, get_error_message
from gersemi.return_codes import FAIL, INTERNAL_ERROR, SUCCESS
from gersemi.task_result import TaskResult
from gersemi.tasks.check_formatting import check_formatting
from gersemi.tasks.check_and_show_diff import check_and_show_diff
from gersemi.tasks.do_nothing import do_nothing
from gersemi.tasks.forward_to_stdout import forward_to_stdout
from gersemi.tasks.format_file import format_file
from gersemi.tasks.rewrite_in_place import rewrite_in_place
from gersemi.tasks.show_diff import show_diff
from gersemi.utils import fromfile, smart_open
from gersemi.keywords import Keywords
from gersemi.warnings import UnknownCommandWarning


CHUNKSIZE = 16


print_to_stdout = partial(print, file=sys.stdout, end="")
print_to_stderr = partial(print, file=sys.stderr)


class WarningSink:
    def __init__(self, quiet):
        self.quiet = quiet
        self.at_least_one_warning_issued = False
        self.records = []

    def __call__(self, s: str):
        self.at_least_one_warning_issued = True
        if not self.quiet:
            self.records.append(s)

    def flush(self):
        for s in self.records:
            print_to_stderr(s)


class StatusCode:
    def __init__(self):
        self.value = SUCCESS

    def __iadd__(self, other):
        if isinstance(other, int):
            self.value = max(self.value, other)
            return self

        if isinstance(other, collections.abc.Iterable):
            for item in other:
                self += item

            return self

        raise RuntimeError(f"Invalid type: {type(other)}")


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


def check_conflicting_definitions(definitions, warning_sink: WarningSink):
    for name, info in definitions.items():
        if len(info) > 1:
            warning_sink(f"Warning: conflicting definitions for '{name}':")
            places = sorted(where for _, where in info)
            for index, where in enumerate(places):
                kind = "(used)   " if index == 0 else "(ignored)"
                warning_sink(f"{kind} {where}")


def find_all_custom_command_definitions(
    paths: Iterable[Path], pool, warning_sink: WarningSink
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
            warning_sink(get_error_message(defs))
            continue

        for name, info in defs.items():
            if name in result:
                result[name].extend(info)
            else:
                result[name] = info

    check_conflicting_definitions(result, warning_sink)

    return get_just_definitions(result)


def select_task(mode: Mode, configuration: Configuration):
    return {
        Mode.ForwardToStdout: forward_to_stdout,
        Mode.RewriteInPlace: rewrite_in_place,
        Mode.CheckFormatting: check_formatting,
        Mode.ShowDiff: partial(show_diff, configuration.control.color),
        Mode.CheckFormattingAndShowDiff: partial(
            check_and_show_diff, configuration.control.color
        ),
    }[mode]


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
    task_result: TaskResult,
    configuration: Configuration,
    warning_sink: WarningSink,
) -> Tuple[Path, int, bool]:
    if task_result.to_stdout != "":
        print_to_stdout(task_result.to_stdout)

    warnings = (
        [w for w in task_result.warnings if not isinstance(w, UnknownCommandWarning)]
        if not configuration.outcome.warn_about_unknown_commands
        else task_result.warnings
    )

    for warning in warnings:
        warning_sink(warning.get_message(fromfile(task_result.path)))

    if task_result.to_stderr != "":
        warning_sink(task_result.to_stderr)

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


def summarize_configuration(configuration, extension_definitions):
    hasher = sha1()
    hasher.update(repr(configuration).encode("utf-8"))
    hasher.update(repr(extension_definitions).encode("utf-8"))
    return hasher.hexdigest()


def split_files_by_formatting_state(
    cache,
    configuration: OutcomeConfiguration,
    files: Iterable[Path],
):
    extension_definitions = load_definitions_from_extensions(configuration.extensions)
    summary = summarize_configuration(configuration, extension_definitions)
    known_files = cache.get_files(summary)
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
    if mode in [
        Mode.CheckFormatting,
        Mode.CheckFormattingAndShowDiff,
        Mode.RewriteInPlace,
    ]:
        cache.store_files(configuration_summary, files)


def select_task_for_already_formatted_files(mode: Mode):
    return {
        Mode.ForwardToStdout: forward_to_stdout,
    }.get(mode, do_nothing)


def handle_already_formatted_files(
    mode: Mode,
    configuration: Configuration,
    warning_sink: WarningSink,
    already_formatted_files: Iterable[Path],
) -> Iterable[int]:
    task = select_task_for_already_formatted_files(mode)
    formatter = NullFormatter()
    execute = partial(run_task, formatter=formatter, task=task)
    results = [
        consume_task_result(result, configuration, warning_sink)
        for result in map(execute, already_formatted_files)
    ]
    return (code for _, code, _ in results)


def handle_files_to_format(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    mode: Mode,
    configuration: Configuration,
    cache,
    pool,
    warning_sink: WarningSink,
    files_to_format: Iterable[Path],
) -> Iterable[int]:
    custom_command_definitions = find_all_custom_command_definitions(
        set(configuration.outcome.definitions), pool, warning_sink
    )
    extension_definitions = load_definitions_from_extensions(
        configuration.outcome.extensions
    )

    formatter = create_formatter(
        configuration.outcome,
        ChainMap(custom_command_definitions, extension_definitions),
    )
    task = select_task(mode, configuration)
    execute = partial(run_task, formatter=formatter, task=task)

    results = [
        consume_task_result(result, configuration, warning_sink)
        for result in pool.imap_unordered(execute, files_to_format, chunksize=CHUNKSIZE)
    ]
    store_files_in_cache(
        mode,
        cache,
        summarize_configuration(configuration.outcome, extension_definitions),
        (
            path
            for path, code, has_warnings in results
            if code == SUCCESS and path != Path("-") and (not has_warnings)
        ),
    )
    return (code for _, code, _ in results)


class GetConfiguration:
    def __init__(
        self,
        args: argparse.Namespace,
        control: ControlConfiguration,
        warning_sink: WarningSink,
    ):
        self.args = args
        self.control = control
        self.processed_configuration_files: List[Path] = []
        self.warning_sink = warning_sink

    def _warn(self, item: NotSupportedKeys, text: str):
        self.warning_sink(f"{item.path}: {text}")

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

    def __call__(self, configuration_file: Optional[Path]) -> Configuration:
        outcome_configuration, not_supported_keys = make_outcome_configuration(
            configuration_file=configuration_file,
            args=self.args,
        )
        self._inform_about_not_supported_keys(not_supported_keys)
        return Configuration(control=self.control, outcome=outcome_configuration)


def split_files_by_configuration_file(
    paths: Iterable[Path], control: ControlConfiguration
):
    if control.configuration_file is not None:
        return {control.configuration_file: paths}

    result = defaultdict(list)
    for path in paths:
        result[find_closest_dot_gersemirc(path)].append(path)

    return result


def print_configuration_report(
    kind: PrintConfigKind,
    buckets: Dict[Optional[Path], Iterable[Path]],
    get_configuration: GetConfiguration,
):
    report = {
        PrintConfigKind.Minimal: lambda conf_file, conf, _: minimal_report(
            conf_file, conf
        ),
        PrintConfigKind.Verbose: verbose_report,
    }.get(kind, lambda *args: None)

    for config_file, target_files in buckets.items():
        config = get_configuration(config_file)
        result = report(config_file, config.outcome, target_files)
        if result is not None:
            print_to_stdout(result)


# pylint: disable=too-many-locals
def run(args: argparse.Namespace):
    try:
        requested_files = get_files(args.sources)
    except FileNotFoundError as e:
        # pylint: disable=broad-exception-raised
        raise Exception(f"Source path doesn't exist: {e.filename}") from e

    mode = get_mode(args)
    control = make_control_configuration(args)
    warning_sink = WarningSink(control.quiet)
    pool_cm = create_pool(
        is_stdin_in_sources=(Path("-") in requested_files),
        workers=control.workers,
    )

    buckets = split_files_by_configuration_file(requested_files, control)
    get_configuration = GetConfiguration(args, control, warning_sink)
    if mode == Mode.PrintConfig:
        print_configuration_report(args.print_config, buckets, get_configuration)
        return SUCCESS

    with create_cache(control.cache) as cache, pool_cm() as pool:
        status_code = StatusCode()
        for config_file, files in buckets.items():
            config = get_configuration(config_file)
            if config.outcome.disable_formatting:
                continue

            already_formatted_files, files_to_format = split_files_by_formatting_state(
                cache, config.outcome, files
            )

            status_code += handle_already_formatted_files(
                mode, config, warning_sink, already_formatted_files
            )
            status_code += handle_files_to_format(
                mode, config, cache, pool, warning_sink, files_to_format
            )

        status_code += (
            FAIL
            if (control.warnings_as_errors and warning_sink.at_least_one_warning_issued)
            else SUCCESS
        )
        warning_sink.flush()
        return status_code.value
