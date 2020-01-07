from gersemi.sanity_checker import drop_comments_and_whitespaces
from .tests_generator import generate_input_only_tests


def test_abstract_syntax_tree_equivalence(parser, formatter, case):
    before_formatting = drop_comments_and_whitespaces(parser.parse(case.content))
    after_formatting = drop_comments_and_whitespaces(
        parser.parse(formatter.format(case.content))
    )

    assert before_formatting.pretty() == after_formatting.pretty()
    assert before_formatting == after_formatting


pytest_generate_tests = generate_input_only_tests(
    where="formatter", input_extension=".in",
)
