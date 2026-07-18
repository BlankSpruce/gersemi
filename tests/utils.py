import gersemi_rust_backend
from gersemi.configuration import Configuration, OutcomeConfiguration


def preprocess(text):
    return (
        text.replace("⟶", "\\⟶")
        .replace("·", "\\·")
        .replace("\t", "⟶")
        .replace(" ", "·")
        .replace("\n", "↵\n")
    )


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
