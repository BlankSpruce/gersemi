from contextlib import contextmanager
from dataclasses import asdict, astuple, dataclass, field, fields
from enum import Enum
from functools import lru_cache
from hashlib import sha1
import multiprocessing
import os
from pathlib import Path
import sys
import textwrap
from typing import Iterable, Optional, Sequence, Tuple, Union
import yaml


def max_number_of_workers():
    result = multiprocessing.cpu_count()
    if sys.platform == "win32":
        # https://bugs.python.org/issue26903
        # https://github.com/python/cpython/issues/89240
        return min(result, 60)
    return result


def doc(text: str) -> str:
    return " ".join(textwrap.dedent(text).splitlines()).strip()


class EnumWithMetadata(Enum):
    def __new__(cls, data):
        self = object.__new__(cls)
        self._value_ = data["value"]
        self.description = doc(data["description"])
        self.title = data["title"]
        return self

    def __repr__(self):
        return self.value


class Tabs(EnumWithMetadata):
    Tabs = dict(
        value="tabs",
        description="Use tabs to indent the code.",
        title="Tab indent",
    )


Spaces = int
Indent = Union[Spaces, Tabs]


def indent_type(thing) -> Indent:
    if thing == Tabs.Tabs.value:
        return Tabs.Tabs

    return max(1, int(thing))


class MaxWorkers(EnumWithMetadata):
    MaxWorkers = dict(
        value="max",
        description="Use maximum possible amount of workers.",
        title="Max workers",
    )


NumberOfWorkers = int
Workers = Union[NumberOfWorkers, MaxWorkers]


def workers_type(thing) -> Workers:
    if thing == MaxWorkers.MaxWorkers.value:
        return MaxWorkers.MaxWorkers

    return min(max(1, int(thing)), max_number_of_workers())


class ListExpansion(EnumWithMetadata):
    FavourInlining = dict(
        value="favour-inlining",
        description="""
    With "favour-inlining" the list of entities will be formatted in such way that sublists
    might still be formatted into single line as long as it's possible or as long as it doesn't
    break the "more than four standalone arguments" heuristic that's mostly focused on commands
    like `set` or `list(APPEND)`.
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
class OutcomeConfiguration:
    """
    These arguments control how gersemi formats source code.
    Values for these arguments can be stored in .gersemirc file which should be
    placed in directory next to the source file or any parent directory with
    priority on closest configuration file.
    Arguments from command line can be used to override parts of that stored
    configuration or supply them in absence of configuration file.
    Precedence: (command line arguments) > (.gersemirc values) > (defaults)
    """

    line_length: int = field(
        default=80,
        metadata=dict(
            title="Line length",
            description="Maximum line length in characters.",
        ),
    )

    indent: Indent = field(
        default=4,
        metadata=dict(
            title="Indent",
            description="Number of spaces used to indent or 'tabs' for indenting with tabs",
        ),
    )

    unsafe: bool = field(
        default=False,
        metadata=dict(
            title="Unsafe",
            description="Skip default sanity checks.",
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

    warn_about_unknown_commands: bool = field(
        default=True,
        metadata=dict(
            title="Warn about unknown commands",
            description=doc(
                """
    When enabled file which has unknown custom commands will have warnings
    issued about that and result won't be cached. See: "Let's make a deal"
    section in README.
                """
            ),
        ),
    )

    def summary(self):
        hasher = sha1()
        hasher.update(repr(self).encode("utf-8"))
        return hasher.hexdigest()


@dataclass
class ControlConfiguration:
    """
    These arguments control how gersemi operates rather than how it formats source code.
    Values for these options are not read from .gersemirc file.
    Default values are used when the arguments aren't supplied.
    Precedence: (command line arguments) > (defaults)
    """

    quiet: bool = field(
        default=False,
        metadata=dict(
            title="Quiet",
            description="Skip printing non-error messages to stderr.",
            command_line_only=True,
        ),
    )

    color: bool = field(
        default=False,
        metadata=dict(
            title="Colorized diff",
            description="If --diff is selected showed diff is colorized.",
            command_line_only=True,
        ),
    )

    workers: Workers = field(
        default=MaxWorkers.MaxWorkers,
        metadata=dict(
            title="Workers",
            description=doc(
                """
    Explicit number of workers or 'max' for maximum possible
    number of workers on given machine used to format multiple
    files in parallel.
                """
            ),
            command_line_only=True,
        ),
    )

    cache: bool = field(
        default=True,
        metadata=dict(
            title="Enable cache",
            description=doc(
                """
    Enables cache with data about files that are known
    to be formatted to speed up execution.
                """
            ),
            command_line_only=True,
        ),
    )


@dataclass
class Configuration:
    outcome: OutcomeConfiguration
    control: ControlConfiguration

    def __hash__(self):
        return hash(astuple(self))


OUTCOME_CONFIGURATION_KEYS = [f.name for f in fields(OutcomeConfiguration)]
CONTROL_CONFIGURATION_KEYS = [f.name for f in fields(ControlConfiguration)]
CONFIGURATION_KEYS = OUTCOME_CONFIGURATION_KEYS + CONTROL_CONFIGURATION_KEYS


def represent_enum_with_metadata(dumper, data):
    return dumper.represent_str(data.value)


yaml.SafeDumper.add_representer(Tabs, represent_enum_with_metadata)
yaml.SafeDumper.add_representer(MaxWorkers, represent_enum_with_metadata)


def make_configuration_file(configuration):
    d = asdict(configuration)
    d["list_expansion"] = d["list_expansion"].value
    result = f"""
# yaml-language-server: $schema=https://raw.githubusercontent.com/BlankSpruce/gersemi/master/gersemi/configuration.schema.json

{yaml.safe_dump(d)}
    """
    return result.strip()


def make_default_configuration_file():
    return make_configuration_file(OutcomeConfiguration())


@lru_cache(maxsize=None)
def find_closest_dot_gersemirc_impl(parent: Path) -> Optional[Path]:
    maybe_found = list(parent.glob(".gersemirc"))
    if maybe_found:
        return maybe_found[0]

    return None


def find_closest_dot_gersemirc(path: Path) -> Optional[Path]:
    for parent in path.parents:
        maybe_found = find_closest_dot_gersemirc_impl(parent)
        if maybe_found:
            return maybe_found

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
    if definitions is None:
        return definitions

    try:
        return tuple(Path(d).resolve(True) for d in definitions)
    except FileNotFoundError as e:
        # pylint: disable=broad-exception-raised
        raise Exception(f"Definition path doesn't exist: {e.filename}") from e


def sanitize_list_expansion(list_expansion):
    if list_expansion is None:
        return list_expansion

    legal_values = [e.value for e in ListExpansion]
    if list_expansion in legal_values:
        return ListExpansion(list_expansion)
    raise RuntimeError(
        f"Unsupported list_expansion: '{list_expansion}'. Legal values: {', '.join(legal_values)}"
    )


@dataclass
class NotSupportedKeys:
    path: Optional[Path] = None
    unknown: Sequence[str] = tuple()
    command_line_only: Sequence[str] = tuple()


def get_not_supported_keys(path, content):
    return NotSupportedKeys(
        path=path.resolve(),
        unknown=[key for key in content if key not in CONFIGURATION_KEYS],
        command_line_only=[key for key in content if key in CONTROL_CONFIGURATION_KEYS],
    )


@lru_cache(maxsize=None)
def load_configuration_from_file(
    configuration_file_path: Optional[Path],
) -> Tuple[OutcomeConfiguration, NotSupportedKeys]:
    if configuration_file_path is None:
        return OutcomeConfiguration(), NotSupportedKeys()

    with enter_directory(configuration_file_path.parent):
        with open(configuration_file_path, "r", encoding="utf-8") as f:
            configuration_file_content = yaml.safe_load(f.read())
            config = {
                key: value
                for key, value in configuration_file_content.items()
                if key in OUTCOME_CONFIGURATION_KEYS
            }
            not_supported_keys = get_not_supported_keys(
                configuration_file_path, configuration_file_content
            )

            if "definitions" in config:
                config["definitions"] = normalize_definitions(config["definitions"])
            if "list_expansion" in config:
                config["list_expansion"] = sanitize_list_expansion(
                    config["list_expansion"]
                )
            if "indent" in config:
                config["indent"] = indent_type(config["indent"])
        return OutcomeConfiguration(**config), not_supported_keys


def override_with_args(configuration, args):
    parameters = [field.name for field in fields(type(configuration))]
    for param in parameters:
        value = getattr(args, param)
        if value is None:
            continue

        setattr(configuration, param, value)
    return configuration


def make_outcome_configuration(
    path, args
) -> Tuple[OutcomeConfiguration, NotSupportedKeys]:
    outcome, not_supported_keys = load_configuration_from_file(
        find_closest_dot_gersemirc(path)
    )

    return override_with_args(outcome, args), not_supported_keys


def make_control_configuration(args) -> ControlConfiguration:
    return override_with_args(ControlConfiguration(), args)
