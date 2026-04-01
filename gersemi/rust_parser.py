import gersemi_rust_parser
from collections import ChainMap
from gersemi.builtin_commands import _builtin_commands


class RustParser:
    def __init__(self):
        self.blocks = ()
        self.known_definitions = {}

    def parse(self, text, known_definitions=None):
        if known_definitions is None:
            known_definitions = {}

        self.blocks = (
            ("if", "endif"),
            ("foreach", "endforeach"),
            ("function", "endfunction"),
            ("macro", "endmacro"),
            ("while", "endwhile"),
            ("block", "endblock"),
            *(
                (name, definition["block_end"])
                for name, definition in known_definitions.items()
                if definition.get("block_end", None)
            ),
        )
        self.known_definitions = (
            _builtin_commands
            if known_definitions is None
            else ChainMap(known_definitions, _builtin_commands)
        )
        self.known_commands = tuple(key for key in self.known_definitions)

        return gersemi_rust_parser.parse(text, self.blocks, self.known_definitions)
