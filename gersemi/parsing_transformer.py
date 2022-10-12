from lark import Token, Tree
from lark.visitors import Transformer
from gersemi.ast_helpers import is_newline
from gersemi.types import Nodes


class DowncaseIdentifiers(Transformer):
    def IDENTIFIER(self, token):
        return Token(
            "IDENTIFIER",
            token.lower(),
            start_pos=token.start_pos,
            line=token.line,
            column=token.column,
            end_line=token.end_line,
            end_column=token.end_column,
        )

    def terminal_as_rule(self, token):
        return self.IDENTIFIER(token[0])


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
    DowncaseIdentifiers, FlattenBracketComment, CleanUpComplexArgument, CleanUpNewlines
):
    pass
