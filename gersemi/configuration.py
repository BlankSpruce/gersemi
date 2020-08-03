from dataclasses import dataclass, fields
from itertools import chain
import os
from pathlib import Path
from typing import Iterable, Optional
import yaml


@dataclass
class Configuration:
    line_length: int = 80
    unsafe: bool = False
    quiet: bool = False
    color: bool = False
    definitions: Iterable[Path] = tuple()


def find_common_parent_path(paths: Iterable[Path]) -> Path:
    return Path(os.path.commonpath([path.absolute() for path in paths]))


def find_dot_gersemirc(paths: Iterable[Path]) -> Optional[Path]:
    lowest_level_common_parent = find_common_parent_path(paths)
    for parent in chain(
        [lowest_level_common_parent], lowest_level_common_parent.parents
    ):
        maybe_found = list(parent.glob(".gersemirc"))
        if maybe_found:
            return maybe_found[0]

    return None


def load_configuration_from_file(configuration_file_path: Path) -> Configuration:
    with open(configuration_file_path, "r") as f:
        config = yaml.safe_load(f.read())
        if "definitions" in config:
            config["definitions"] = [Path(d) for d in config["definitions"]]

        return Configuration(**config)


def override_configuration_with_args(
    configuration: Configuration, args
) -> Configuration:
    parameters = [field.name for field in fields(Configuration)]
    for param in parameters:
        value = getattr(args, param)
        if value:
            setattr(configuration, param, value)
    return configuration


def make_configuration(args) -> Configuration:
    configuration_file_path = find_dot_gersemirc(args.sources)
    if configuration_file_path is not None:
        result = load_configuration_from_file(configuration_file_path)
    else:
        result = Configuration()

    return override_configuration_with_args(result, args)
