import os
from lark import Lark, UnexpectedInput
from gersemi.exceptions import (
    GenericParsingError,
    UnbalancedParentheses,
    UnbalancedBrackets,
)
from gersemi.parsing_transformer import ParsingTransformer
from gersemi.postprocessor import PostProcessor


class Parser:
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
            "foo(commented_argument #foobar)",
            "foo(commented_argument #[[foobar]]",
            "foo(almost_commented_argument #)",
        ],
    }

    def __init__(self, grammar_filename):
        self.lark_parser = Lark.open(
            grammar_filename=grammar_filename,
            parser="lalr",
            propagate_positions=False,
            maybe_placeholders=False,
            transformer=ParsingTransformer(),
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


class ParserWithPostProcessing:
    def __init__(self, parser):
        self.parser = parser

    def parse(self, code):
        postprocessor = PostProcessor(code)
        return postprocessor.transform(self.parser.parse(code))


HERE = os.path.dirname(os.path.realpath(__file__))
GRAMMAR = os.path.join(HERE, "cmake.lark")


def create_parser(grammar_filename=GRAMMAR):
    return Parser(grammar_filename)


def create_parser_with_postprocessing(bare_parser):
    return ParserWithPostProcessing(bare_parser)


BARE_PARSER = create_parser()
PARSER = create_parser_with_postprocessing(BARE_PARSER)
