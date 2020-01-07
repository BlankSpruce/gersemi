from gersemi.dumper import DumpToString
from gersemi.postprocessor import PostProcessor
from gersemi.sanity_checker import check_code_equivalence


def get_terminal_patterns(parser):
    return {terminal.name: terminal.pattern.value for terminal in parser.terminals}


def noop(*_):
    pass


class Formatter:  # pylint: disable=too-few-public-methods
    def __init__(self, parser, sanity_checker):
        self.parser = parser
        self.sanity_checker = sanity_checker

    def _parse(self, code):
        postprocessor = PostProcessor(code, get_terminal_patterns(self.parser))
        return postprocessor.transform(self.parser.parse(code))

    def format(self, code):
        result = DumpToString().visit(self._parse(code))
        self.sanity_checker(self.parser, code, result)
        return result


def create_formatter(parser, do_sanity_check):
    sanity_checker = check_code_equivalence if do_sanity_check else noop
    return Formatter(parser, sanity_checker)
