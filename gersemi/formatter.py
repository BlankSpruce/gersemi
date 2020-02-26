from gersemi.configuration import Configuration
from gersemi.dumper import Dumper
from gersemi.postprocessor import PostProcessor
from gersemi.sanity_checker import check_code_equivalence


def noop(*_):
    pass


class Formatter:  # pylint: disable=too-few-public-methods
    def __init__(self, parser, sanity_checker, configuration: Configuration):
        self.parser = parser
        self.sanity_checker = sanity_checker
        self.configuration = configuration

    def _parse(self, code):
        postprocessor = PostProcessor(
            code, self.configuration.preserve_custom_command_formatting
        )
        return postprocessor.transform(self.parser.parse(code))

    def format(self, code):
        dumper = Dumper(self.configuration.line_length)
        result = dumper.visit(self._parse(code))
        self.sanity_checker(self.parser, code, result)
        return result


def create_formatter(
    parser, do_sanity_check, line_length, preserve_custom_command_formatting=True,
):
    sanity_checker = check_code_equivalence if do_sanity_check else noop
    return Formatter(
        parser,
        sanity_checker,
        Configuration(line_length, preserve_custom_command_formatting),
    )
