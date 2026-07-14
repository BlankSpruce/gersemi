import argparse
from collections import defaultdict
import collections.abc
from functools import partial
from pathlib import Path
import sys
from typing import Dict, Iterable, Optional
import gersemi_rust_backend
from gersemi.configuration import (
    Configuration,
    ControlConfiguration,
    find_closest_dot_gersemirc,
    make_control_configuration,
    make_outcome_configuration,
)
from gersemi.configuration_reports import minimal_report, verbose_report
from gersemi.custom_command_definition_finder import get_just_definitions
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
        gersemi_rust_backend.find_all_custom_command_definitions(
            configuration,
            warning_sink,
        )
    )


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
    args: argparse.Namespace,
    buckets: Dict[Optional[Path], Iterable[Path]],
    control: ControlConfiguration,
    warning_sink,
):
    report = {
        PrintConfigKind.Minimal: lambda conf_file, conf, _: minimal_report(
            conf_file, conf
        ),
        PrintConfigKind.Verbose: verbose_report,
    }.get(args.print_config, lambda *args: None)

    for config_file, target_files in buckets.items():
        config = Configuration(
            control=control,
            outcome=make_outcome_configuration(config_file, args, warning_sink),
        )
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
    app = gersemi_rust_backend.App(mode, control)
    warning_sink = gersemi_rust_backend.WarningSink(control.quiet)

    buckets = split_files_by_configuration_file(requested_files, control)
    if mode == Mode.PrintConfig:
        print_configuration_report(args, buckets, control, warning_sink)
        return SUCCESS

    status_code = StatusCode()
    for config_file, files in buckets.items():
        config = Configuration(
            control=control,
            outcome=make_outcome_configuration(config_file, args, warning_sink),
        )
        if config.outcome.disable_formatting:
            continue

        status_code += app.handle_files(warning_sink, config, list(files))

    status_code += (
        FAIL
        if (control.warnings_as_errors and warning_sink.at_least_one_warning_issued)
        else SUCCESS
    )
    warning_sink.flush()
    return status_code.value
