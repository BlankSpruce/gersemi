from gersemi.configuration import OutcomeConfiguration
from gersemi.custom_command_definition_finder import (
    find_custom_command_definitions,
    get_just_definitions,
)
from gersemi.dumper import Dumper
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


def create_dumper(custom_command_definitions):
    return Dumper(
        configuration=OutcomeConfiguration(line_length=80, indent=4),
        known_definitions=custom_command_definitions,
    )


def test_custom_command_generated_dumper(
    parser_with_postprocessing, case
):  # pylint: disable=redefined-outer-name
    parsed_function_def = parser_with_postprocessing.parse(case.content)
    definitions = get_just_definitions(
        find_custom_command_definitions(parsed_function_def)
    )

    parsed_function = parser_with_postprocessing.parse(
        custom_command_to_format, definitions
    )
    dumper = create_dumper(definitions)
    custom_command_formatted = dumper.visit(parsed_function)

    assert custom_command_formatted == custom_command_properly_formatted


pytest_generate_tests = generate_input_only_tests(
    where="custom_command_formatting", input_extension=".cmake"
)
