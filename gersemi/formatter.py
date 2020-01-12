from gersemi.dumper import Dumper
from gersemi.experimental.line_comment_reflower import LineCommentReflower
from gersemi.experimental.dumper import Dumper as ExperimentalDumper
from gersemi.postprocessor import PostProcessor
from gersemi.sanity_checker import check_code_equivalence


def get_terminal_patterns(parser):
    return {terminal.name: terminal.pattern.value for terminal in parser.terminals}


def noop(*_):
    pass


class Formatter:  # pylint: disable=too-few-public-methods
    def __init__(self, parser, sanity_checker, enable_experimental_features):
        self.parser = parser
        self.sanity_checker = sanity_checker
        self.enable_experimental_features = enable_experimental_features

    def _get_line_comment_reflower(self, code):
        if self.enable_experimental_features:
            return LineCommentReflower(code)
        return None

    def _parse(self, code):
        postprocessor = PostProcessor(
            get_terminal_patterns(self.parser), self._get_line_comment_reflower(code)
        )
        return postprocessor.transform(self.parser.parse(code))

    def format(self, code):
        dumper = ExperimentalDumper() if self.enable_experimental_features else Dumper()
        result = dumper.visit(self._parse(code))
        self.sanity_checker(self.parser, code, result)
        return result


def create_formatter(parser, do_sanity_check, enable_experimental_features=False):
    sanity_checker = check_code_equivalence if do_sanity_check else noop
    return Formatter(parser, sanity_checker, enable_experimental_features)
