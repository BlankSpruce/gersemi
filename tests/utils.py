from collections import ChainMap
from gersemi.builtin_commands import _builtin_commands
from gersemi.configuration import OutcomeConfiguration
import gersemi.dumper
import gersemi.parser


def preprocess(text):
    return (
        text.replace("⟶", "\\⟶")
        .replace("·", "\\·")
        .replace("\t", "⟶")
        .replace(" ", "·")
        .replace("\n", "↵\n")
    )


class Dumper(gersemi.dumper.Dumper):
    def __init__(self, known_definitions=None):
        super().__init__(
            configuration=OutcomeConfiguration(line_length=80, indent=4),
            known_definitions=ChainMap(
                {} if known_definitions is None else known_definitions,
                _builtin_commands,
            ),
        )


class Parser(gersemi.parser.Parser):
    def __init__(self, known_definitions=None):
        super().__init__(
            ChainMap(
                {} if known_definitions is None else known_definitions,
                _builtin_commands,
            )
        )
