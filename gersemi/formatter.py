from gersemi.dumper import DumpToString
from gersemi.postprocessor import PostProcessor


def get_terminal_patterns(parser):
    return {terminal.name: terminal.pattern.value for terminal in parser.terminals}


class Formatter:  # pylint: disable=too-few-public-methods
    def __init__(self, parser):
        self.parser = parser

    def _parse(self, code):
        postprocessor = PostProcessor(code, get_terminal_patterns(self.parser))
        return postprocessor.transform(self.parser.parse(code))

    def format(self, code):
        return DumpToString().visit(self._parse(code))


def create_formatter(parser):
    return Formatter(parser)
