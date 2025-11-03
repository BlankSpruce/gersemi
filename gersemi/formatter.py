from copy import deepcopy
from typing import Tuple
from gersemi.configuration import OutcomeConfiguration
from gersemi.dumper import Dumper
from gersemi.noop import noop
from gersemi.parser import BARE_PARSER
from gersemi.postprocessor import postprocess
from gersemi.sanity_checker import check_code_equivalence
from gersemi.warnings import FormatterWarnings


GERSEMI_OFF = "# gersemi: off"
GERSEMI_ON = "# gersemi: on"


def consume_until(iterator, target):
    while True:
        line = next(iterator, None)
        if line is None:
            return None

        if line.strip() == target:
            return line


def reconstruct_disabled_formatting_zones_impl(original, formatted):
    other = iter(original.splitlines(keepends=True))
    active = iter(formatted.splitlines(keepends=True))

    while True:
        line = next(active, None)
        if line is None:
            break

        command = line.strip()
        if command == GERSEMI_OFF:
            consume_until(other, command)
            other, active = active, other

        if command == GERSEMI_ON:
            gersemi_on = consume_until(other, command)
            if gersemi_on is not None:
                line = gersemi_on
            other, active = active, other

        yield line


def reconstruct_disabled_formatting_zones(original, formatted):
    if GERSEMI_OFF not in original:
        return formatted

    return "".join(reconstruct_disabled_formatting_zones_impl(original, formatted))


class Formatter:
    def __init__(
        self, configuration: OutcomeConfiguration, sanity_checker, known_definitions
    ):
        self.configuration = configuration
        self.sanity_checker = sanity_checker
        self.known_definitions = known_definitions

    def format(self, code) -> Tuple[str, FormatterWarnings]:
        tree = BARE_PARSER.parse(code, self.known_definitions)
        original = deepcopy(tree)
        dumper = Dumper(self.configuration, self.known_definitions)
        result = dumper.visit(postprocess(code, self.known_definitions, tree))
        self.sanity_checker(BARE_PARSER, original, result)
        return (
            reconstruct_disabled_formatting_zones(code, result),
            dumper.get_warnings(),
        )


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
