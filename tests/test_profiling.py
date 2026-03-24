import pytest
from gersemi.exceptions import ParsingError
from .tests_generator import generate_input_only_tests


def test_profile_parser_with_postprocessing(parser, case):
    try:
        parser.parse(case.content)
    except ParsingError:
        pytest.fail("invalid input to parse")
        raise


pytest_generate_tests = generate_input_only_tests(
    where="formatter", input_extension=".in.cmake"
)
