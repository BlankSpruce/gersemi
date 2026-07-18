import gersemi_rust_backend
import pytest
from .tests_generator import generate_input_only_tests


def test_parser(case):
    try:
        gersemi_rust_backend.validate(case.content)
    except BaseException:
        pytest.fail("invalid input to parse")
        raise


GenericParsingError = "unspecified parsing error"
UnbalancedParentheses = "unbalanced parentheses"
UnbalancedBrackets = "unbalanced brackets"
UnbalancedBlock = "unbalanced block"


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
def test_invalid_code_parsing_error(invalid_code, expected_exception):
    with pytest.raises(RuntimeError) as rust_exc_info:
        gersemi_rust_backend.validate(invalid_code)

    assert expected_exception in str(rust_exc_info.value)


pytest_generate_tests = generate_input_only_tests(
    where="parser", input_extension=".cmake"
)
