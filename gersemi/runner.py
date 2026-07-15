import argparse
from collections import defaultdict
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
from gersemi.mode import Mode, get_mode
from gersemi.print_config_kind import PrintConfigKind
from gersemi.return_codes import SUCCESS


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
            outcome=make_outcome_configuration(config_file, args),
        )
        result = report(config_file, config.outcome, target_files)
        if result is not None:
            print(result, file=sys.stdout, end="")


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
    buckets = split_files_by_configuration_file(requested_files, control)
    if mode == Mode.PrintConfig:
        print_configuration_report(args, buckets, control)
        return SUCCESS

    for config_file, files in buckets.items():
        config = Configuration(
            control=control,
            outcome=make_outcome_configuration(config_file, args),
        )
        if config.outcome.disable_formatting:
            continue

        app.handle_files(config, list(files))

    app.handle_warnings()
    return app.status_code()
