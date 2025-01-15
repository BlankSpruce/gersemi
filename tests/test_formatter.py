import pytest
from gersemi.exceptions import ASTMismatch
from gersemi.sanity_checker import check_code_equivalence
from tests.utils import preprocess
from tests.tests_generator import generate_input_output_tests


def test_formatter(formatter_creator, case):
    p = preprocess
    formatter = formatter_creator(case.config)
    formatted_once, _ = formatter.format(case.given)
    assert p(formatted_once) == p(case.expected)


def test_formatter_idempotence(formatter_creator, case):
    p = preprocess
    formatter = formatter_creator(case.config)
    formatted_once, _ = formatter.format(case.given)
    formatted_twice, _ = formatter.format(formatted_once)
    assert p(formatted_once) == p(formatted_twice)


def test_abstract_syntax_tree_equivalence(parser, parser_with_simple_grammar, case):
    for p in [parser, parser_with_simple_grammar]:
        try:
            parsed = p.parse(case.given)
            check_code_equivalence(p, parsed, case.expected)
        except ASTMismatch:
            pytest.fail("ASTs mismatch")
            raise


pytest_generate_tests = generate_input_output_tests(
    where="formatter", input_extension=".in.cmake", output_extension=".out.cmake"
)
