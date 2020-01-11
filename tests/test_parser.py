import pytest
import lark
from .tests_generator import generate_input_only_tests


def test_parser(parser, case):
    try:
        parser.parse(case.content)
    except lark.UnexpectedInput:
        pytest.fail("invalid input to parse")
        raise


pytest_generate_tests = generate_input_only_tests(
    where="parser", input_extension=".cmake",
)
