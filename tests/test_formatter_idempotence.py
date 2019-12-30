from .tests_generator import generate_input_only_tests


def test_formatter_idempotence(formatter, case):
    formatted_once = formatter.format(case.content)
    formatted_twice = formatter.format(formatted_once)
    assert formatted_once == formatted_twice


pytest_generate_tests = generate_input_only_tests(
    where="formatter", input_extension=".in",
)
