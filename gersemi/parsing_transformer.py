from lark import Token, Tree
from lark.visitors import Transformer
from gersemi.ast_helpers import is_newline
from gersemi.types import Nodes


class FlattenBracketComment(Transformer):
    def bracket_comment(self, children) -> Tree:
        *_, bracket_argument = children
        return Tree("bracket_comment", bracket_argument.children)


class CleanUpComplexArgument(Transformer):
    def complex_argument(self, children):
        return Tree("complex_argument", children[1:-1])


class CleanUpNewlines(Transformer):
    def newline_or_gap(self, children):
        return Token("NEWLINE", "".join(children)[:2])

    def arguments(self, children: Nodes) -> Tree:
        return Tree("arguments", [child for child in children if not is_newline(child)])


class ParsingTransformer(
    FlattenBracketComment, CleanUpComplexArgument, CleanUpNewlines
):
    pass
