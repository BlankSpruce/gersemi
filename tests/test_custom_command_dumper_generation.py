from gersemi.custom_command_definition_finder import (
    find_custom_command_definitions,
    get_just_definitions,
)
from tests.utils import Dumper, Parser
from .tests_generator import generate_input_only_tests

custom_command_to_format = """
seven_samurai(
three standalone arguments
KAMBEI KATSUSHIRO
GOROBEI foo HEIHACHI bar KYUZO baz
SHICHIROJI foo bar baz KIKUCHIYO bar baz foo)
"""

custom_command_properly_formatted = """Seven_Samurai(
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


def test_custom_command_generated_dumper(case):  # pylint: disable=redefined-outer-name
    definitions = get_just_definitions(find_custom_command_definitions(case.content))

    after = Parser(known_definitions=definitions)
    parsed_function = after.parse(custom_command_to_format)
    dumper = Dumper(definitions)
    custom_command_formatted = dumper.visit(parsed_function)

    assert custom_command_formatted == custom_command_properly_formatted


pytest_generate_tests = generate_input_only_tests(
    where="custom_command_formatting", input_extension=".cmake"
)
