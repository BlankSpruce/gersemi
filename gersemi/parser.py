from dataclasses import astuple, dataclass
from functools import lru_cache
import os
from typing import Sequence
from lark import Lark, UnexpectedInput
from gersemi.exceptions import (
    GenericParsingError,
    UnbalancedParentheses,
    UnbalancedBrackets,
)
from gersemi.parsing_transformer import ParsingTransformer
from gersemi.postprocessor import postprocess


@dataclass
class CustomBlock:
    start: str
    end: str

    def __hash__(self):
        return hash(astuple(self))

    def rule(self, index) -> str:
        return f"""
        _custom_block__{index}: _block_template{{CB_BEGIN_{index}, CB_END_{index}}}
        CB_BEGIN_{index}: "{self.start.lower()}"i
        CB_END_{index}: "{self.end.lower()}"i

        %extend block: _custom_block__{index}
        """


def create_custom_rules(custom_blocks: Sequence[CustomBlock]) -> str:
    return "\n".join(block.rule(index) for index, block in enumerate(custom_blocks))


@lru_cache(maxsize=None)
def get_lark_parser(grammar_filename, custom_blocks: Sequence[CustomBlock]) -> Lark:
    with open(grammar_filename, encoding="utf-8") as f:
        grammar_as_string = f.read()
        grammar_as_string += create_custom_rules(custom_blocks)

        return Lark(
            grammar=grammar_as_string,
            parser="lalr",
            propagate_positions=False,
            maybe_placeholders=False,
            transformer=ParsingTransformer(),
        )


class Parser:
    examples = {
        UnbalancedBrackets: [
            "foo(foo [[foo]=]",
            "foo([=[foo bar]])",
            "foo([=[foo bar ]==])",
            "foo(foo [=[foo bar ]==] foo)",
            "foo(foo foo [==[foo]===] foo)",
        ],
        UnbalancedParentheses: [
            "foo(foo foo",
            "foo(foo foo # )",
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
        self.grammar_filename = grammar_filename

    def _match_parsing_error(self, lark_parser, code, exception):
        specific_error = exception.match_examples(lark_parser.parse, self.examples)
        if not specific_error:
            raise GenericParsingError(
                exception.get_context(code), exception.line, exception.column
            )
        raise specific_error(
            exception.get_context(code), exception.line, exception.column
        )

    def parse(  # pylint: disable=inconsistent-return-statements
        self, code, known_definitions=None
    ):
        if known_definitions:
            custom_blocks = tuple(
                CustomBlock(start=n, end=d["block_end"])
                for n, d in known_definitions.items()
                if d.get("block_end", None)
            )
        else:
            custom_blocks = tuple()

        lark_parser = get_lark_parser(self.grammar_filename, custom_blocks)

        try:
            return lark_parser.parse(code)
        except UnexpectedInput as u:
            self._match_parsing_error(lark_parser, code, u)


class ParserWithPostProcessing:
    def __init__(self, parser):
        self.parser = parser

    def parse(self, code, known_definitions=None):
        return postprocess(code, known_definitions, self.parser.parse(code))


HERE = os.path.dirname(os.path.realpath(__file__))
GRAMMAR = os.path.join(HERE, "cmake.lark")


def create_parser(grammar_filename=GRAMMAR):
    return Parser(grammar_filename)


def create_parser_with_postprocessing(bare_parser):
    return ParserWithPostProcessing(bare_parser)


BARE_PARSER = create_parser()
PARSER = create_parser_with_postprocessing(BARE_PARSER)
