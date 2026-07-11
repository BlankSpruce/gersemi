import gersemi_rust_backend
from gersemi.configuration import Configuration, OutcomeConfiguration
import gersemi.parser
from gersemi.runner import find_all_custom_command_definitions


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


class Formatter:
    def __init__(self, definitions):
        configuration = Configuration(
            outcome=OutcomeConfiguration(
                line_length=80, indent=4, definitions=definitions
            )
        )
        self.impl = gersemi_rust_backend.Formatter(
            configuration=configuration,
            definition_schemas=find_all_custom_command_definitions(
                configuration=configuration,
            ),
            lines_to_format=[],
        )

    def format(self, code):
        return self.impl.format(code)
