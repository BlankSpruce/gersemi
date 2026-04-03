import pytest
from gersemi.exceptions import (
    GenericParsingError,
    ParsingError,
    UnbalancedBlock,
    UnbalancedBrackets,
    UnbalancedParentheses,
)
from .tests_generator import generate_input_only_tests


def test_parser(lark_based_parser, rust_parser, parser, case):
    try:
        lark_based_parser.parse(case.content)
        parser.parse(case.content)
        rust_parser.parse(case.content)
    except ParsingError:
        pytest.fail("invalid input to parse")
        raise


@pytest.mark.parametrize(
    ("invalid_code", "expected_exception"),
    [
        ("set(FOO BAR", UnbalancedParentheses),
        ("message(FOO BAR (BAZ AND FOO)", UnbalancedParentheses),
        ("set(FOO BAR # )", UnbalancedParentheses),
        ("bar)", UnbalancedParentheses),
        ("bar(FOO BAR (BAZ OR FOO)))", UnbalancedParentheses),
        ("another_command #(", UnbalancedParentheses),
        ("foo_command bar_command", UnbalancedParentheses),
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
        (
            """function()
function()
set(")
endfunction()
endfunction()
""",
            GenericParsingError,
        ),
    ],
)
def test_invalid_code_parsing_error(
    lark_based_parser, rust_parser, parser, invalid_code, expected_exception
):
    with pytest.raises(ParsingError) as lark_based_exc_info:
        lark_based_parser.parse(invalid_code)

    assert lark_based_exc_info.type is expected_exception

    with pytest.raises(ParsingError) as handwritten_exc_info:
        parser.parse(invalid_code)

    assert handwritten_exc_info.type is expected_exception

    with pytest.raises(ParsingError) as rust_exc_info:
        rust_parser.parse(invalid_code)

    assert rust_exc_info.type is expected_exception

    assert handwritten_exc_info.value.args == rust_exc_info.value.args


pytest_generate_tests = generate_input_only_tests(
    where="parser", input_extension=".cmake"
)
