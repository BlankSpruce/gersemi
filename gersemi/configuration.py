from contextlib import contextmanager
from dataclasses import asdict, dataclass, field, fields
from enum import Enum
from hashlib import sha1
from itertools import chain
import os
from pathlib import Path
import textwrap
from typing import Iterable, Optional
import yaml


def doc(text: str) -> str:
    return " ".join(textwrap.dedent(text).splitlines()).strip()


class EnumWithMetadata(Enum):
    def __new__(cls, data):
        self = object.__new__(cls)
        self._value_ = data["value"]
        self.description = doc(data["description"])
        self.title = data["title"]
        return self


class ListExpansion(EnumWithMetadata):
    FavourInlining = dict(
        value="favour-inlining",
        description="""
    With "favour-inlining" the list of entities will be formatted in such way that sublists
    might still be formatted into single line as long as it's possible.
        """,
        title="Favour inlining",
    )
    FavourExpansion = dict(
        value="favour-expansion",
        description="""
    With "favour-expansion" the list of entities will be formatted in such way that sublists
    will be completely expanded once expansion becomes necessary at all.
        """,
        title="Favour expansion",
    )


@dataclass
class Configuration:
    """
    By default configuration is loaded from YAML formatted .gersemirc file if it's available.
    This file should be placed in one of the common parent directories of source files.
    Arguments from command line can be used to override parts of that configuration or
    supply them in absence of configuration file.
    """

    line_length: int = field(
        default=80,
        metadata=dict(
            title="Line length",
            description="Maximum line length in characters.",
        ),
    )

    unsafe: bool = field(
        default=False,
        metadata=dict(
            title="Unsafe",
            description="Skip default sanity checks.",
        ),
    )

    quiet: bool = field(
        default=False,
        metadata=dict(
            title="Quiet",
            description="Skip printing non-error messages to stderr.",
        ),
    )

    color: bool = field(
        default=False,
        metadata=dict(
            title="Colorized diff",
            description="If --diff is selected showed diff is colorized.",
        ),
    )

    definitions: Iterable[Path] = field(
        default=tuple(),
        metadata=dict(
            title="Definitions",
            description=doc(
                """
    Files or directories containing custom command definitions (functions or macros).
    If only - is provided custom definitions, if there are any, are taken from stdin instead.
    Commands from not deprecated CMake native modules don't have to be provided.
    See: https://cmake.org/cmake/help/latest/manual/cmake-modules.7.html
                """
            ),
        ),
    )

    list_expansion: ListExpansion = field(
        default=ListExpansion.FavourInlining,
        metadata=dict(
            title="List expansion",
            description=doc(
                """
    Switch controls how code is expanded into multiple lines
    when it's not possible to keep it formatted in one line.
                """
            ),
        ),
    )

    def summary(self):
        hasher = sha1()
        hasher.update(repr(self).encode("utf-8"))
        return hasher.hexdigest()


def make_default_configuration_file():
    default_configuration = Configuration()
    d = asdict(default_configuration)
    d["list_expansion"] = d["list_expansion"].value
    result = f"""
# yaml-language-server: $schema=https://raw.githubusercontent.com/BlankSpruce/gersemi/master/gersemi/configuration.schema.json

{yaml.safe_dump(d)}
    """
    return result.strip()


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
