import os
from lark import Lark, Token
from lark.visitors import Transformer


class DowncaseIdentifiers(Transformer):
    def IDENTIFIER(self, token):
        return Token("IDENTIFIER", token.lower())


def create_parser():
    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    return Lark.open(
        grammar_filename=os.path.join(this_file_dir, "cmake.lark"),
        parser="lalr",
        propagate_positions=True,
        maybe_placeholders=False,
        transformer=DowncaseIdentifiers(),
    )
