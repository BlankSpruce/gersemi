from lark import Token, Tree
from lark.visitors import Transformer


class DowncaseIdentifiers(Transformer):
    def IDENTIFIER(self, token):
        return Token(
            "IDENTIFIER",
            token.lower(),
            pos_in_stream=token.pos_in_stream,
            line=token.line,
            column=token.column,
            end_line=token.end_line,
            end_column=token.end_column,
        )


class RestructureBracketTypeRules(Transformer):
    def _split_bracket_argument(self, arg):
        bracket_length = arg.index("[", 1) + 1
        return (
            arg[:bracket_length],
            arg[bracket_length:-bracket_length],
            arg[-bracket_length:],
        )

    def bracket_argument(self, children):
        token, *_ = children
        bracket_open, content, bracket_close = self._split_bracket_argument(token)
        return Tree(
            "bracket_argument",
            [
                Token("bracket_argument_begin", bracket_open),
                Token("bracket_argument_body", content),
                Token("bracket_argument_end", bracket_close),
            ],
        )

    def bracket_comment(self, children) -> Tree:
        *_, bracket_argument = children
        bracket_open, content, bracket_close = bracket_argument.children
        return Tree(
            "bracket_comment",
            [
                Token("bracket_comment_begin", f"#{bracket_open}"),
                Token("bracket_comment_body", content),
                Token("bracket_comment_end", bracket_close),
            ],
        )


class ParsingTransformer(DowncaseIdentifiers, RestructureBracketTypeRules):
    pass
