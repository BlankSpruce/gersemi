from typing import Tuple
from gersemi.configuration import Indent, ListExpansion
from gersemi.dumper import Dumper
from gersemi.parser import BARE_PARSER, PARSER
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
        custom_command_definitions,
        list_expansion: ListExpansion,
    ):
        self.sanity_checker = sanity_checker
        self.line_length = line_length
        self.indent_type = indent
        self.custom_command_definitions = custom_command_definitions
        self.list_expansion = list_expansion

    def format(self, code) -> Tuple[str, FormatterWarnings]:
        dumper = Dumper(
            self.line_length,
            self.indent_type,
            self.custom_command_definitions,
            self.list_expansion,
        )
        result = dumper.visit(PARSER.parse(code))
        self.sanity_checker(BARE_PARSER, code, result)
        return result, dumper.get_warnings()


class NullFormatter:
    def format(self, code):
        return code, []


def create_formatter(
    do_sanity_check,
    line_length,
    indent,
    custom_command_definitions,
    list_expansion,
):
    sanity_checker = check_code_equivalence if do_sanity_check else noop
    return Formatter(
        sanity_checker,
        line_length,
        indent,
        custom_command_definitions,
        list_expansion,
    )
