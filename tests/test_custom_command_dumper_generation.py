from gersemi.custom_command_dumper_generator import generate_custom_command_dumpers
from gersemi.dumper import Dumper
from gersemi.postprocessor import PostProcessor
from .tests_generator import generate_input_only_tests


def parse_and_postprocess(parser, code):
    postprocessor = PostProcessor(code, preserve_custom_command_formatting=False)
    return postprocessor.transform(parser.parse(code))


custom_command_to_format = """
seven_samurai(
KAMBEI KATSUSHIRO
GOROBEI foo HEIHACHI bar KYUZO baz
SHICHIROJI foo bar baz KIKUCHIYO bar baz foo)
"""

custom_command_properly_formatted = """seven_samurai(
    KAMBEI
    KATSUSHIRO
    GOROBEI foo
    HEIHACHI bar
    KYUZO baz
    SHICHIROJI foo bar baz
    KIKUCHIYO bar baz foo
)
"""


def create_patched_dumper(generated_formatter):
    class Impl(generated_formatter, Dumper):
        pass

    return Impl(width=80)


def test_custom_command_generated_dumper(parser, case):
    parsed_function_def = parse_and_postprocess(parser, case.content)
    parsed_function = parse_and_postprocess(parser, custom_command_to_format)

    formatters = generate_custom_command_dumpers(parsed_function_def)
    dumper = create_patched_dumper(formatters["seven_samurai"])

    custom_command_formatted = dumper.visit(parsed_function)

    assert custom_command_formatted == custom_command_properly_formatted


pytest_generate_tests = generate_input_only_tests(
    where="custom_command_formatting", input_extension=".cmake"
)
