from gersemi.dumper import Dumper
from gersemi.parser import create_parser_with_postprocessing
from gersemi.sanity_checker import check_code_equivalence


def noop(*_):
    pass


class Formatter:
    def __init__(
        self, bare_parser, sanity_checker, line_length: int, custom_command_definitions,
    ):
        self.bare_parser = bare_parser
        self.parser = create_parser_with_postprocessing(self.bare_parser)
        self.sanity_checker = sanity_checker
        self.line_length = line_length
        self.custom_command_definitions = custom_command_definitions

    def format(self, code):
        dumper = Dumper(self.line_length, self.custom_command_definitions)
        result = dumper.visit(self.parser.parse(code))
        self.sanity_checker(self.bare_parser, code, result)
        return result


def create_formatter(
    bare_parser, do_sanity_check, line_length, custom_command_definitions
):
    sanity_checker = check_code_equivalence if do_sanity_check else noop
    return Formatter(
        bare_parser, sanity_checker, line_length, custom_command_definitions
    )
