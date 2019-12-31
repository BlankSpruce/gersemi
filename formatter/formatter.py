from formatter.dumper import DumpToString
from formatter.postprocessor import PostProcessor


class Formatter:  # pylint: disable=too-few-public-methods
    def __init__(self, parser):
        self.parser = parser

    def _parse(self, code):
        postprocessor = PostProcessor(code)
        return postprocessor.transform(self.parser.parse(code))

    def format(self, code):
        return DumpToString().visit(self._parse(code))


def create_formatter(parser):
    return Formatter(parser)
