from .tests_generator import generate_input_output_tests


def test_formatter(formatter, case):
    assert formatter.format(case.given) == case.expected


pytest_generate_tests = generate_input_output_tests(
    where="formatter", input_extension=".in", output_extension=".out",
)
