import pytest
from gersemi.custom_command_dumper_generator import generate_custom_command_dumpers
from gersemi.dumper import Dumper
from gersemi.parser import create_parser_with_postprocessing
from .tests_generator import generate_input_only_tests


custom_command_to_format = """
seven_samurai(
three standalone arguments
KAMBEI KATSUSHIRO
GOROBEI foo HEIHACHI bar KYUZO baz
SHICHIROJI foo bar baz KIKUCHIYO bar baz foo)
"""

custom_command_properly_formatted = """seven_samurai(
    three
    standalone
    arguments
    KAMBEI
    KATSUSHIRO
    GOROBEI foo
    HEIHACHI bar
    KYUZO baz
    SHICHIROJI foo bar baz
    KIKUCHIYO bar baz foo
)
"""


@pytest.fixture
def parser_with_postprocessing(parser):
    return create_parser_with_postprocessing(parser)


def create_patched_dumper(generated_formatter):
    class Impl(generated_formatter, Dumper):
        pass

    return Impl(width=80, custom_command_dumpers=dict())


def test_custom_command_generated_dumper(
    parser_with_postprocessing, case
):  # pylint: disable=redefined-outer-name
    parsed_function_def = parser_with_postprocessing.parse(case.content)
    parsed_function = parser_with_postprocessing.parse(custom_command_to_format)

    formatters = generate_custom_command_dumpers(parsed_function_def)
    dumper = create_patched_dumper(formatters["seven_samurai"])

    custom_command_formatted = dumper.visit(parsed_function)

    assert custom_command_formatted == custom_command_properly_formatted


pytest_generate_tests = generate_input_only_tests(
    where="custom_command_formatting", input_extension=".cmake"
)
