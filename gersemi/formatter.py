from collections import ChainMap, defaultdict
from typing import Tuple
import gersemi_rust_backend
from gersemi.builtin_commands import _builtin_commands
from gersemi.configuration import LineRanges, OutcomeConfiguration
from gersemi.warnings import FormatterWarnings, UnknownCommandWarning


class Formatter:
    def __init__(
        self,
        configuration: OutcomeConfiguration,
        known_definitions,
        lines_to_format: LineRanges,
    ):
        self.configuration = configuration
        self.known_definitions = dict(ChainMap(known_definitions, _builtin_commands))
        self.lines_to_format = list(lines_to_format)
        self.init_backend()

    def init_backend(self):
        self.impl = gersemi_rust_backend.Formatter(
            self.configuration, self.known_definitions, self.lines_to_format
        )

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["impl"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.init_backend()

    def get_warnings(self, raw):
        warnings = defaultdict(list)
        for name, line, column in raw:
            warnings[name].append((line, column))

        return [
            UnknownCommandWarning(command_name=name, positions=positions)
            for name, positions in warnings.items()
        ]

    def format(self, code) -> Tuple[str, FormatterWarnings]:
        result, raw_warnings = self.impl.format(code)
        return result, self.get_warnings(raw_warnings)


class NullFormatter:
    def format(self, code):
        return code, []


def create_formatter(
    configuration: OutcomeConfiguration,
    known_definitions,
    lines_to_format,
):
    return Formatter(configuration, known_definitions, lines_to_format)
