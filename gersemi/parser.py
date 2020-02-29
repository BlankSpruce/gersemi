import os
from lark import Lark, Token, UnexpectedInput
from lark.visitors import Transformer
from gersemi.exceptions import (
    GenericParsingError,
    UnbalancedParentheses,
    UnbalancedBrackets,
)
from gersemi.postprocessor import PostProcessor


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


class Parser:  # pylint: disable=too-few-public-methods
    examples = {
        UnbalancedBrackets: [
            "foo(foo [[foo]=]",
            "foo([=[foo bar]])",
            "foo([=[foo bar ]==])",
            "foo(foo [=[foo bar ]==] foo)",
        ],
        UnbalancedParentheses: [
            "foo(bar",
            "foo(bar\n",
            "foo(BAR (BAZ)",
            "foo(# )",
            "foo(bar))",
            "foo)",
            "foo(BAR (BAZ)))",
            "foo(BAR (BAZ FOO)))",
            "foo",
            "foo # (",
        ],
    }

    def __init__(self):
        this_file_dir = os.path.dirname(os.path.realpath(__file__))
        self.lark_parser = Lark.open(
            grammar_filename=os.path.join(this_file_dir, "cmake.lark"),
            parser="lalr",
            propagate_positions=True,
            maybe_placeholders=False,
            transformer=DowncaseIdentifiers(),
        )

    def _match_parsing_error(self, code, exception):
        specific_error = exception.match_examples(self.lark_parser.parse, self.examples)
        if not specific_error:
            raise GenericParsingError(
                exception.get_context(code), exception.line, exception.column
            )
        raise specific_error(
            exception.get_context(code), exception.line, exception.column
        )

    def parse(self, code):
        try:
            return self.lark_parser.parse(code)
        except UnexpectedInput as u:
            self._match_parsing_error(code, u)


class ParserWithPostProcessing:  # pylint: disable=too-few-public-methods
    def __init__(self, parser):
        self.parser = parser

    def parse(self, code):
        postprocessor = PostProcessor(code)
        return postprocessor.transform(self.parser.parse(code))


def create_parser():
    return Parser()


def create_parser_with_postprocessing(bare_parser):
    return ParserWithPostProcessing(bare_parser)
