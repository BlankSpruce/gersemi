import os
from lark import Lark, UnexpectedInput
from lark.grammar import Rule
from lark.lark import LarkOptions
from lark.lexer import TerminalDef
from lark.utils import SerializeMemoizer
from gersemi.exceptions import (
    GenericParsingError,
    UnbalancedParentheses,
    UnbalancedBrackets,
)
from gersemi.parsing_transformer import ParsingTransformer
from gersemi.postprocessor import PostProcessor


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

    # similar function available since lark 0.8.6
    def _recreate_lark_parser(self, data, memo):
        # pylint: disable=protected-access
        deserialized_memo = SerializeMemoizer.deserialize(
            memo, {"Rule": Rule, "TerminalDef": TerminalDef}, {}
        )
        instance = Lark.__new__(Lark)
        options = dict(data["options"])
        options["transformer"] = ParsingTransformer()
        instance.options = LarkOptions.deserialize(options, deserialized_memo)
        instance.rules = [
            Rule.deserialize(rule, deserialized_memo) for rule in data["rules"]
        ]
        instance._prepare_callbacks()
        instance.parser = instance.parser_class.deserialize(
            data["parser"],
            deserialized_memo,
            instance._callbacks,
            instance.options.postlex,
        )
        return instance

    def __getstate__(self):
        return self.lark_parser.memo_serialize([TerminalDef, Rule])

    def __setstate__(self, state):
        data, memo = state
        self.lark_parser = self._recreate_lark_parser(data, memo)


class ParserWithPostProcessing:  # pylint: disable=too-few-public-methods
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
