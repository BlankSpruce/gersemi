import gersemi_rust_backend


class Parser:
    def __init__(self, known_definitions=None):
        self.known_definitions = {} if known_definitions is None else known_definitions

    def parse(self, text):
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
                    for name, definition in self.known_definitions.items()
                    if getattr(definition, "block_end", None)
                ),
            ),
            known_commands=tuple(key for key in self.known_definitions),
        )
