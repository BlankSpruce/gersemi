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


class MergeQuotedArgumentTokens(Transformer_InPlace):
    def quoted_argument(self, children):
        if len(children) < 2:
            return Tree("quoted_argument", children)

        quote_begin, *_, quote_end = children
        token = Token("QUOTED_ARGUMENT", "".join(children))
        token.start_pos = quote_begin.start_pos
        token.end_pos = quote_end.end_pos
        return Tree("quoted_argument", [token])


class ParsingTransformer(
    CleanUpComplexArgument,
    CleanUpNewlines,
    MergeQuotedArgumentTokens,
):
    pass
