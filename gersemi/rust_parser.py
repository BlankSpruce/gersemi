from collections import ChainMap
import gersemi_rust_parser
from gersemi.builtin_commands import _builtin_commands
from gersemi.exceptions import (
    GenericParsingError,
    ParsingError,
    UnbalancedBlock,
    UnbalancedBrackets,
    UnbalancedParentheses,
)
from gersemi.types import Token, Tree

RustErrorType = gersemi_rust_parser.ErrorType
RustToken = gersemi_rust_parser.Node.Token
RustSuccess = gersemi_rust_parser.ParsingResult.Success


def convert(node):
    if isinstance(node, RustToken):
        return Token(node.type_, node.value)

    return Tree(node.data, list(map(convert, node.children)))


def get_exception_type(error_type):
    if error_type == RustErrorType.UnbalancedParentheses:
        return UnbalancedParentheses

    if error_type == RustErrorType.UnbalancedBrackets:
        return UnbalancedBrackets

    if error_type == RustErrorType.UnbalancedBlock:
        return UnbalancedBlock

    if error_type == RustErrorType.ParsingError:
        return ParsingError

    if error_type == RustErrorType.GenericParsingError:
        return GenericParsingError

    return ParsingError


def raise_exception(error):
    exception_type = get_exception_type(error.error_type)
    raise exception_type(error.explanation, error.line, error.column)


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

        result = gersemi_rust_parser.parse(
            text,
            blocks=(
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
            ),
            known_commands=tuple(key for key in self.known_definitions),
        )

        if isinstance(result, RustSuccess):
            return convert(result[0])

        return raise_exception(result)
