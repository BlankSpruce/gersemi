import gersemi_rust_backend
from gersemi.configuration import Configuration, OutcomeConfiguration
from gersemi.exceptions import ASTMismatch


def preprocess(text):
    return (
        text.replace("⟶", "\\⟶")
        .replace("·", "\\·")
        .replace("\t", "⟶")
        .replace(" ", "·")
        .replace("\n", "↵\n")
    )


class Parser:
    def __init__(self, known_definitions=None):
        self.known_definitions = dict(
            {} if known_definitions is None else known_definitions
        )

    def check_code_equivalence(self, before, after):
        if not gersemi_rust_backend.check_code_equivalence(
            self.known_definitions, before, after
        ):
            raise ASTMismatch

    def validate(self, text):
        return gersemi_rust_backend.validate(text, self.known_definitions)


class Formatter:
    def __init__(self, definitions):
        configuration = Configuration(
            outcome=OutcomeConfiguration(
                line_length=80, indent=4, definitions=definitions
            )
        )
        self.impl = gersemi_rust_backend.Formatter(configuration=configuration)

    def format(self, code):
        return self.impl.format(code)
