from lark import Token, Tree
from gersemi.ast_helpers import is_newline
from gersemi.transformer import Transformer_InPlace
from gersemi.types import Nodes


class CleanUpComplexArgument(Transformer_InPlace):
    def complex_argument(self, children):
        return Tree("complex_argument", children[1:-1])


class CleanUpNewlines(Transformer_InPlace):
    def newline_or_gap(self, children):
        return Token("NEWLINE", "".join(children)[:2])

    def arguments(self, children: Nodes) -> Tree:
        return Tree("arguments", [child for child in children if not is_newline(child)])


class ParsingTransformer(CleanUpComplexArgument, CleanUpNewlines):
    pass
