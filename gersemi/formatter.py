from copy import deepcopy
from typing import Tuple
from gersemi.configuration import Indent, ListExpansion
from gersemi.dumper import Dumper
from gersemi.parser import BARE_PARSER
from gersemi.postprocessor import postprocess
from gersemi.sanity_checker import check_code_equivalence
from gersemi.warnings import FormatterWarnings


def noop(*_):
    pass


class Formatter:
    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        sanity_checker,
        line_length: int,
        indent: Indent,
        known_definitions,
        list_expansion: ListExpansion,
    ):
        self.sanity_checker = sanity_checker
        self.line_length = line_length
        self.indent_type = indent
        self.known_definitions = known_definitions
        self.list_expansion = list_expansion

    def format(self, code) -> Tuple[str, FormatterWarnings]:
        tree = BARE_PARSER.parse(code)
        original = deepcopy(tree)
        dumper = Dumper(
            self.line_length,
            self.indent_type,
            self.known_definitions,
            self.list_expansion,
        )
        result = dumper.visit(postprocess(code, self.known_definitions, tree))
        self.sanity_checker(BARE_PARSER, original, result)
        return result, dumper.get_warnings()


class NullFormatter:
    def format(self, code):
        return code, []


def create_formatter(
    do_sanity_check, line_length, indent, known_definitions, list_expansion
):
    sanity_checker = check_code_equivalence if do_sanity_check else noop
    return Formatter(
        sanity_checker,
        line_length,
        indent,
        known_definitions,
        list_expansion,
    )
