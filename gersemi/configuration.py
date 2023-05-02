from contextlib import contextmanager
from dataclasses import asdict, dataclass, fields
from enum import Enum
from hashlib import sha1
from itertools import chain
import os
from pathlib import Path
from typing import Iterable, Optional
import yaml


class ListExpansion(Enum):
    FavourInlining = "favour-inlining"
    FavourExpansion = "favour-expansion"


@dataclass
class Configuration:
    line_length: int = 80
    unsafe: bool = False
    quiet: bool = False
    color: bool = False
    definitions: Iterable[Path] = tuple()
    list_expansion: ListExpansion = ListExpansion.FavourInlining

    def summary(self):
        hasher = sha1()
        hasher.update(repr(self).encode("utf-8"))
        return hasher.hexdigest()


def make_default_configuration_file():
    default_configuration = Configuration()
    d = asdict(default_configuration)
    d["list_expansion"] = d["list_expansion"].value
    return yaml.safe_dump(d)


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


@contextmanager
def enter_directory(target_directory):
    original = Path(".").resolve()
    try:
        os.chdir(target_directory)
        yield
    finally:
        os.chdir(original)


def normalize_definitions(definitions):
    return [Path(d).resolve() for d in definitions]


def sanitize_list_expansion(list_expansion):
    legal_values = [e.value for e in ListExpansion]
    if list_expansion in legal_values:
        return ListExpansion(list_expansion)
    raise RuntimeError(
        f"Unsupported list_expansion: '{list_expansion}'. Legal values: {', '.join(legal_values)}"
    )


def load_configuration_from_file(configuration_file_path: Path) -> Configuration:
    with enter_directory(configuration_file_path.parent):
        with open(configuration_file_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f.read())
            if "definitions" in config:
                config["definitions"] = normalize_definitions(config["definitions"])
            if "list_expansion" in config:
                config["list_expansion"] = sanitize_list_expansion(
                    config["list_expansion"]
                )
        return Configuration(**config)


def override_configuration_with_args(
    configuration: Configuration, args
) -> Configuration:
    parameters = [field.name for field in fields(Configuration)]
    for param in parameters:
        value = getattr(args, param)
        if not value:
            continue
        if param == "definitions":
            value = normalize_definitions(value)
        if param == "list_expansion":
            value = sanitize_list_expansion(value)
        setattr(configuration, param, value)
    return configuration


def make_configuration(args) -> Configuration:
    configuration_file_path = find_dot_gersemirc(args.sources)
    if configuration_file_path is not None:
        result = load_configuration_from_file(configuration_file_path)
    else:
        result = Configuration()

    return override_configuration_with_args(result, args)
