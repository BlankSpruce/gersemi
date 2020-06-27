from gersemi.custom_command_definition_finder import find_custom_command_definitions
from gersemi.dumper import Dumper
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


def create_dumper(custom_command_definitions):
    return Dumper(width=80, custom_command_definitions=custom_command_definitions)


def test_custom_command_generated_dumper(
    parser_with_postprocessing, case
):  # pylint: disable=redefined-outer-name
    parsed_function_def = parser_with_postprocessing.parse(case.content)
    parsed_function = parser_with_postprocessing.parse(custom_command_to_format)

    formatters = find_custom_command_definitions(parsed_function_def)
    dumper = create_dumper(formatters)

    custom_command_formatted = dumper.visit(parsed_function)

    assert custom_command_formatted == custom_command_properly_formatted


pytest_generate_tests = generate_input_only_tests(
    where="custom_command_formatting", input_extension=".cmake"
)
