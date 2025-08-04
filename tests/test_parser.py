import pytest
from gersemi.exceptions import (
    ParsingError,
    UnbalancedParentheses,
    UnbalancedBrackets,
    UnbalancedBlock,
)
from .tests_generator import generate_input_only_tests


def test_parser(parser, case):
    try:
        parser.parse(case.content)
    except ParsingError:
        pytest.fail("invalid input to parse")
        raise


@pytest.mark.parametrize(
    ["invalid_code", "expected_exception"],
    [
        ("set(FOO BAR", UnbalancedParentheses),
        ("message(FOO BAR (BAZ AND FOO)", UnbalancedParentheses),
        ("set(FOO BAR # )", UnbalancedParentheses),
        ("bar)", UnbalancedParentheses),
        ("bar(FOO BAR (BAZ OR FOO)))", UnbalancedParentheses),
        ("another_command #(", UnbalancedParentheses),
        ("foo_command", UnbalancedParentheses),
        ("foo([[foo]=])", UnbalancedBrackets),
        ("foo([=[bar]])", UnbalancedBrackets),
        ("foo(arg1 arg2 [==[arg3]===] arg4)", UnbalancedBrackets),
        ("macro(foobar)", UnbalancedBlock),
        ("function(foobar)", UnbalancedBlock),
        (
            """function()
            set(FOO foo)""",
            UnbalancedBlock,
        ),
        (
            """function(foobar)
            set(FOO foo)""",
            UnbalancedBlock,
        ),
        (
            """function()
    set(SETTING "FOO")""",
            UnbalancedBlock,
        ),
        (
            """if()
    set(SETTING "FOO")
elseif()
    set(SETTING "BAR")""",
            UnbalancedBlock,
        ),
        (
            """if()
    set(SETTING "FOO")
elseif()
    set(SETTING "BAR")
else()
    set(SETTING "BAR")""",
            UnbalancedBlock,
        ),
        (
            """if()
    set(SETTING "FOO")
else()
    set(SETTING "BAR")""",
            UnbalancedBlock,
        ),
    ],
)
def test_invalid_code_parsing_error(parser, invalid_code, expected_exception):
    try:
        parser.parse(invalid_code)
        raise AssertionError("Parser should throw an exception")
    except ParsingError as e:
        assert isinstance(e, expected_exception)


pytest_generate_tests = generate_input_only_tests(
    where="parser", input_extension=".cmake"
)
