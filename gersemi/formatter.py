from gersemi.dumper import Dumper
from gersemi.parser import BARE_PARSER, PARSER
from gersemi.sanity_checker import check_code_equivalence


def noop(*_):
    pass


class Formatter:
    def __init__(self, sanity_checker, line_length: int, custom_command_definitions):
        self.sanity_checker = sanity_checker
        self.line_length = line_length
        self.custom_command_definitions = custom_command_definitions

    def format(self, code):
        dumper = Dumper(self.line_length, self.custom_command_definitions)
        result = dumper.visit(PARSER.parse(code))
        self.sanity_checker(BARE_PARSER, code, result)
        return result


def create_formatter(do_sanity_check, line_length, custom_command_definitions):
    sanity_checker = check_code_equivalence if do_sanity_check else noop
    return Formatter(sanity_checker, line_length, custom_command_definitions)
