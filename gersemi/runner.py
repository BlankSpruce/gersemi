import argparse
from pathlib import Path
import sys
from typing import Iterable, Optional, Tuple
import gersemi_rust_backend
from gersemi.configuration import (
    Configuration,
    make_control_configuration,
    make_outcome_configuration,
)
from gersemi.configuration_reports import minimal_report, verbose_report
from gersemi.print_config_kind import PrintConfigKind
from gersemi.return_codes import SUCCESS


def print_configuration_report(
    args: argparse.Namespace,
    buckets: Iterable[Tuple[Optional[Path], Iterable[Path]]],
):
    control = make_control_configuration(args)
    report = {
        PrintConfigKind.Minimal: lambda conf_file, conf, _: minimal_report(
            conf_file, conf
        ),
        PrintConfigKind.Verbose: verbose_report,
    }.get(args.print_config, lambda *args: None)

    for config_file, target_files in buckets:
        config = Configuration(
            control=control,
            outcome=make_outcome_configuration(config_file, args),
        )
        result = report(config_file, config.outcome, target_files)
        if result is not None:
            print(result, file=sys.stdout, end="")


# pylint: disable=too-many-locals
def run(args: argparse.Namespace):
    app = gersemi_rust_backend.App(args)
    buckets = app.get_source_file_buckets()
    if app.is_print_config_mode():
        print_configuration_report(args, buckets)
        return SUCCESS

    return app.run(buckets)
