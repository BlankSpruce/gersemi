from collections import ChainMap
import gersemi_rust_backend
from gersemi.builtin_commands import _builtin_commands


class RustParser:
    def __init__(self):
        self.blocks = ()
        self.known_definitions = {}

    def parse(self, text, known_definitions=None):
        if known_definitions is None:
            known_definitions = {}

        self.known_definitions = (
            _builtin_commands
            if known_definitions is None
            else ChainMap(known_definitions, _builtin_commands)
        )

        return gersemi_rust_backend.parse(
            text,
            blocks=(
                ("if", "endif"),
                ("foreach", "endforeach"),
                ("function", "endfunction"),
                ("macro", "endmacro"),
                ("while", "endwhile"),
                ("block", "endblock"),
                *(
                    (name, definition.block_end)
                    for name, definition in known_definitions.items()
                    if getattr(definition, "block_end", None)
                ),
            ),
            known_commands=tuple(key for key in self.known_definitions),
        )
