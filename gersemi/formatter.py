from copy import deepcopy
from functools import lru_cache
import re
from typing import List, Tuple
from gersemi.configuration import LineRanges, OutcomeConfiguration
from gersemi.dumper import Dumper
from gersemi.noop import noop
from gersemi.parser import BARE_PARSER
from gersemi.postprocessor import postprocess
from gersemi.sanity_checker import check_code_equivalence
from gersemi.warnings import FormatterWarnings


GERSEMI_OFF = "# gersemi: off"
GERSEMI_ON = "# gersemi: on"
BUG = "#-#-# gersemi: If you see this there is a bug in gersemi, please report it.#-#-#"
LINE_RANGE_FENCE_OFF = f"{GERSEMI_OFF}\n{BUG}\n"
LINE_RANGE_FENCE_ON = f"{BUG}\n{GERSEMI_ON}\n"


@lru_cache(maxsize=None)
def line_range_fence_regex():
    off_pattern = f"[ \t]*{GERSEMI_OFF}\\n{BUG}\\n"
    on_pattern = f"{BUG}\\n[ \t]*{GERSEMI_ON}\\n"
    return re.compile(f"{off_pattern}|{on_pattern}")


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


def add_line_range_fences_impl(lines: List[str], lines_to_format: LineRanges):
    N = len(lines)

    starts = [r.start for r in lines_to_format]
    ends = [r.end for r in lines_to_format]

    if 1 not in starts:
        yield LINE_RANGE_FENCE_OFF

    for line_number, line in enumerate(lines, start=1):
        if (line_number in starts) and (line_number != 1):
            yield LINE_RANGE_FENCE_ON

        yield line

        if (line_number in ends) and (line_number != N):
            yield LINE_RANGE_FENCE_OFF

    if N not in ends:
        yield LINE_RANGE_FENCE_ON


def add_line_range_fences(code: str, lines_to_format: LineRanges) -> str:
    lines = code.splitlines(keepends=True)
    N = len(lines)
    if N < max(r.end for r in lines_to_format):
        return code

    return "".join(add_line_range_fences_impl(lines, lines_to_format))


def remove_line_range_fences(formatted_code: str) -> str:
    pattern = line_range_fence_regex()
    return pattern.sub("", formatted_code)


class Formatter:
    def __init__(
        self,
        configuration: OutcomeConfiguration,
        sanity_checker,
        known_definitions,
        lines_to_format: LineRanges,
    ):
        self.configuration = configuration
        self.sanity_checker = sanity_checker
        self.known_definitions = known_definitions
        self.lines_to_format = lines_to_format

    def format(self, code) -> Tuple[str, FormatterWarnings]:
        if self.lines_to_format:
            code = add_line_range_fences(code, self.lines_to_format)

        tree = BARE_PARSER.parse(code, self.known_definitions)
        original = deepcopy(tree)
        dumper = Dumper(self.configuration, self.known_definitions)
        formatted = dumper.visit(postprocess(code, self.known_definitions, tree))
        self.sanity_checker(BARE_PARSER, original, formatted)

        result = reconstruct_disabled_formatting_zones(code, formatted)
        if self.lines_to_format:
            result = remove_line_range_fences(result)

        return result, dumper.get_warnings()


class NullFormatter:
    def format(self, code):
        return code, []


def create_formatter(
    configuration: OutcomeConfiguration,
    known_definitions,
    lines_to_format,
):
    sanity_checker = check_code_equivalence if not configuration.unsafe else noop
    return Formatter(
        configuration,
        sanity_checker,
        known_definitions,
        lines_to_format,
    )
