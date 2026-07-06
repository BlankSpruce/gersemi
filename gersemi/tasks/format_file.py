from collections import defaultdict
from pathlib import Path
from typing import Optional
import gersemi_rust_backend
from gersemi.formatted_file import FormattedFile
from gersemi.warnings import unknown_command_warning


def process_warnings(path, raw_warnings):
    warnings = defaultdict(list)
    for name, line, column in raw_warnings:
        warnings[name].append((line, column))

    return [
        unknown_command_warning(command_name=name, positions=positions, filepath=path)
        for name, positions in warnings.items()
    ]


def format_file(
    path: Path,
    formatter: Optional[gersemi_rust_backend.Formatter],
    warn_about_unknown_commands: bool,
) -> FormattedFile:
    code, formatted_code, newlines_style, warnings = gersemi_rust_backend.format_file(
        path=path, formatter=formatter
    )

    return FormattedFile(
        before=code,
        after=formatted_code,
        newlines_style=newlines_style,
        path=path,
        warnings=process_warnings(path, warnings)
        if warn_about_unknown_commands
        else [],
    )
