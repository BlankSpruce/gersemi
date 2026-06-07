from dataclasses import dataclass
import gersemi_rust_backend
from gersemi.exceptions import ASTMismatch


@dataclass
class ParserDefinitions:
    blocks: list
    known_commands: list

    @staticmethod
    def from_dict(definitions):
        return ParserDefinitions(
            blocks=(
                ("if", "endif"),
                ("foreach", "endforeach"),
                ("function", "endfunction"),
                ("macro", "endmacro"),
                ("while", "endwhile"),
                ("block", "endblock"),
                *(
                    (name, definition.block_end)
                    for name, definition in definitions.items()
                    if getattr(definition, "block_end", None)
                ),
            ),
            known_commands=tuple(definitions.keys()),
        )


class Parser:
    def __init__(self, known_definitions=None):
        self.known_definitions = ParserDefinitions.from_dict(
            {} if known_definitions is None else known_definitions
        )

    def check_code_equivalence(self, before, after):
        if not gersemi_rust_backend.check_code_equivalence(
            self.known_definitions, before, after
        ):
            raise ASTMismatch

    def parse(self, text):
        return gersemi_rust_backend.parse(text, self.known_definitions)
