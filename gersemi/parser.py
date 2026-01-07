from dataclasses import astuple, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Sequence
from lark import Lark, UnexpectedInput
from gersemi.exceptions import (
    GenericParsingError,
    UnbalancedParentheses,
    UnbalancedBrackets,
    UnbalancedBlock,
    UnbalancedQuotes,
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


@lru_cache(maxsize=None)
def block_examples(block_start):
    return (
        f"{block_start}()",
        f"""{block_start}()
foobar()""",
        f"""{block_start}()
foobar(FOO foo)""",
        f"""{block_start}()
set(FOO "foo")""",
        f"""{block_start}()
""",
        f"""{block_start}()
foobar()
""",
        f"""{block_start}()
foobar(FOO foo)
""",
        f"""{block_start}()
set(FOO "foo")
""",
    )


class Parser:
    static_examples = {
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
        UnbalancedBlock: [
            """if()
        else()""",
            """if()
        foo()
        else()"""
            """if()
                    elseif()
            set(FOO foo)""",
            """if()
            foo()
                    elseif()
            set(FOO foo)""",
            """if()
                    elseif()
            set(FOO foo)
                    else()
            set(FOO foo)""",
            """if()
        else()
""",
            """if()
        foo()
        else()
"""
            """if()
                    elseif()
            set(FOO foo)
""",
            """if()
            foo()
                    elseif()
            set(FOO foo)
""",
            """if()
                    elseif()
            set(FOO foo)
                    else()
            set(FOO foo)
""",
        ],
        UnbalancedQuotes: [
            'set(foo ")',
            """set(foo ")
""",
        ],
    }
    static_block_starts = (
        "block",
        "foreach",
        "function",
        "if",
        "macro",
        "while",
    )

    def __init__(self, grammar_filename):
        self.grammar_filename = grammar_filename

    def _match_parsing_error(self, lark_parser, code, custom_blocks, exception):
        specific_error = exception.match_examples(
            lark_parser.parse,
            self.examples(custom_blocks),
            use_accepts=False,
        )

        if not specific_error:
            raise GenericParsingError(
                exception.get_context(code), exception.line, exception.column
            )
        raise specific_error(
            exception.get_context(code), exception.line, exception.column
        )

    def examples(self, custom_blocks):
        result = self.static_examples.copy()
        ub = UnbalancedBlock

        for block_start in self.static_block_starts:
            if ub not in result:
                result[ub] = block_examples(block_start)
            else:
                result[ub].extend(block_examples(block_start))

        for block in custom_blocks:
            if ub not in result:
                result[ub] = block_examples(block.start)
            else:
                result[ub].extend(block_examples(block.start))

        return result

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
            custom_blocks = ()

        lark_parser = get_lark_parser(self.grammar_filename, custom_blocks)

        try:
            return lark_parser.parse(code)
        except UnexpectedInput as u:
            self._match_parsing_error(lark_parser, code, custom_blocks, u)


class ParserWithPostProcessing:
    def __init__(self, parser):
        self.parser = parser

    def parse(self, code, known_definitions=None):
        return postprocess(code, known_definitions, self.parser.parse(code))


HERE = Path(__file__).resolve().parent
GRAMMAR = HERE / "cmake.lark"


def create_parser(grammar_filename=GRAMMAR):
    return Parser(grammar_filename)


def create_parser_with_postprocessing(bare_parser):
    return ParserWithPostProcessing(bare_parser)


BARE_PARSER = create_parser()
PARSER = create_parser_with_postprocessing(BARE_PARSER)
