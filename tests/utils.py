from gersemi.configuration import OutcomeConfiguration
import gersemi.formatter
import gersemi.parser


def preprocess(text):
    return (
        text.replace("⟶", "\\⟶")
        .replace("·", "\\·")
        .replace("\t", "⟶")
        .replace(" ", "·")
        .replace("\n", "↵\n")
    )


class Parser(gersemi.parser.Parser):
    def __init__(self, known_definitions=None):
        super().__init__(
            {} if known_definitions is None else known_definitions,
        )


class Formatter(gersemi.formatter.Formatter):
    def __init__(self, known_definitions=None):
        super().__init__(
            configuration=OutcomeConfiguration(line_length=80, indent=4),
            known_definitions={} if known_definitions is None else known_definitions,
            lines_to_format=(),
        )
