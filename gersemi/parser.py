import gersemi_rust_backend
from gersemi.exceptions import ASTMismatch


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
