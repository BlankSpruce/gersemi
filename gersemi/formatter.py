from copy import deepcopy
from typing import Tuple
from gersemi.configuration import OutcomeConfiguration
from gersemi.dumper import Dumper
from gersemi.noop import noop
from gersemi.parser import BARE_PARSER
from gersemi.postprocessor import postprocess
from gersemi.sanity_checker import check_code_equivalence
from gersemi.warnings import FormatterWarnings


class Formatter:
    def __init__(
        self, configuration: OutcomeConfiguration, sanity_checker, known_definitions
    ):
        self.configuration = configuration
        self.sanity_checker = sanity_checker
        self.known_definitions = known_definitions

    def format(self, code) -> Tuple[str, FormatterWarnings]:
        tree = BARE_PARSER.parse(code)
        original = deepcopy(tree)
        dumper = Dumper(self.configuration, self.known_definitions)
        result = dumper.visit(postprocess(code, self.known_definitions, tree))
        self.sanity_checker(BARE_PARSER, original, result)
        return result, dumper.get_warnings()


class NullFormatter:
    def format(self, code):
        return code, []


def create_formatter(configuration: OutcomeConfiguration, known_definitions):
    sanity_checker = check_code_equivalence if not configuration.unsafe else noop
    return Formatter(
        configuration,
        sanity_checker,
        known_definitions,
    )
