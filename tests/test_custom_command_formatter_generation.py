from tests.utils import Formatter
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


def test_custom_command_generated_formatter(case, tmp_path):  # pylint: disable=redefined-outer-name
    definition_file = tmp_path / "definition.cmake"
    definition_file.write_text(case.content)
    formatter = Formatter(definitions=[definition_file])
    custom_command_formatted, _ = formatter.format(custom_command_to_format)

    assert custom_command_formatted == custom_command_properly_formatted


pytest_generate_tests = generate_input_only_tests(
    where="custom_command_formatting", input_extension=".cmake"
)
