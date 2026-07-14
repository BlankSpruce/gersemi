import argparse
from collections import defaultdict
import collections.abc
from functools import partial
from hashlib import sha1
from pathlib import Path
import sys
from typing import Dict, Iterable, List, Optional
import gersemi_rust_backend
from gersemi.cache import create_cache
from gersemi.configuration import (
    Configuration,
    ControlConfiguration,
    NotSupportedKeys,
    OutcomeConfiguration,
    find_closest_dot_gersemirc,
    make_control_configuration,
    make_outcome_configuration,
)
from gersemi.configuration_reports import minimal_report, verbose_report
from gersemi.custom_command_definition_finder import get_just_definitions
from gersemi.extensions import load_definitions_from_extensions
from gersemi.keywords import Keywords
from gersemi.mode import Mode, get_mode
from gersemi.print_config_kind import PrintConfigKind
from gersemi.return_codes import FAIL, SUCCESS

CHUNKSIZE = 250
FILE_PATTERNS = ("CMakeLists.txt", "CMakeLists.txt.in", "*.cmake", "*.cmake.in")


print_to_stdout = partial(print, file=sys.stdout, end="")
print_to_stderr = partial(print, file=sys.stderr)


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


def find_all_custom_command_definitions(
    configuration: Configuration,
    warning_sink=None,
) -> Dict[str, Keywords]:
    return get_just_definitions(
        dict(
            gersemi_rust_backend.find_all_custom_command_definitions(
                list(set(configuration.outcome.definitions)),
                warning_sink,
                configuration,
            )
        )
    )


def summarize_configuration(configuration):
    extension_definitions = load_definitions_from_extensions(configuration.extensions)
    hasher = sha1()
    hasher.update(repr(configuration).encode("utf-8"))
    hasher.update(repr(extension_definitions).encode("utf-8"))
    return hasher.hexdigest()


def split_files_by_formatting_state(
    cache,
    configuration: OutcomeConfiguration,
    files: Iterable[Path],
):
    return gersemi_rust_backend.split_files_by_formatting_state(
        cache, list(files), summarize_configuration(configuration)
    )


def handle_files_to_format(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    mode: Mode,
    configuration: Configuration,
    cache,
    warning_sink,
    files_to_format: Iterable[Path],
) -> Iterable[int]:
    custom_command_definitions = find_all_custom_command_definitions(
        configuration, warning_sink
    )
    return gersemi_rust_backend.handle_files_to_format(
        mode,
        configuration,
        warning_sink,
        files_to_format,
        custom_command_definitions,
        summarize_configuration(configuration.outcome),
        cache,
    )


class GetConfiguration:
    def __init__(
        self,
        args: argparse.Namespace,
        control: ControlConfiguration,
        warning_sink,
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
    control = make_control_configuration(args)
    requested_files = gersemi_rust_backend.get_files(
        paths=list(args.sources),
        respect_ignore_files=control.respect_ignore_files,
    )

    if args.line_ranges and len(requested_files) > 1:
        # pylint: disable=broad-exception-raised
        raise Exception("Line range formatting available only with one source file")

    mode = get_mode(args)
    warning_sink = gersemi_rust_backend.WarningSink(control.quiet)

    buckets = split_files_by_configuration_file(requested_files, control)
    get_configuration = GetConfiguration(args, control, warning_sink)
    if mode == Mode.PrintConfig:
        print_configuration_report(args.print_config, buckets, get_configuration)
        return SUCCESS

    enable_cache = control.cache and (not control.line_ranges)
    with create_cache(enable_cache, control.cache_dir) as cache:
        status_code = StatusCode()
        for config_file, files in buckets.items():
            config = get_configuration(config_file)
            if config.outcome.disable_formatting:
                continue

            already_formatted_files, files_to_format = split_files_by_formatting_state(
                cache, config.outcome, files
            )

            status_code += gersemi_rust_backend.handle_already_formatted_files(
                mode, config, warning_sink, already_formatted_files
            )
            status_code += handle_files_to_format(
                mode, config, cache, warning_sink, files_to_format
            )

        status_code += (
            FAIL
            if (control.warnings_as_errors and warning_sink.at_least_one_warning_issued)
            else SUCCESS
        )
        warning_sink.flush()
        return status_code.value
