import gersemi_rust_backend
from tests.tests_generator import generate_input_output_tests
from tests.utils import preprocess


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


def test_abstract_syntax_tree_equivalence(case):
    assert gersemi_rust_backend.check_code_equivalence(case.given, case.expected)


pytest_generate_tests = generate_input_output_tests(
    where="formatter", input_extension=".in.cmake", output_extension=".out.cmake"
)
