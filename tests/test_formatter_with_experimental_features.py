import pytest
from lark import Discard
from lark.visitors import Transformer
from gersemi.sanity_checker import drop_whitespaces
from .tests_generator import generate_input_output_tests


@pytest.fixture(scope="module")
def experimental_enabled():
    return True


def drop_comments(tree):
    class Impl(Transformer):  # pylint: disable=too-few-public-methods
        def _drop_node(self, _):
            raise Discard()

        non_command_element = _drop_node
        line_comment = _drop_node
        bracket_comment = _drop_node

    return Impl().transform(tree)


def drop_comments_and_whitespaces(tree):
    return drop_comments(drop_whitespaces(tree))


def test_formatter(formatter, case):
    assert formatter.format(case.given) == case.expected


def test_formatter_idempotence(formatter, case):
    formatted_once = formatter.format(case.given)
    formatted_twice = formatter.format(formatted_once)
    assert formatted_once == formatted_twice


def test_abstract_syntax_tree_equivalence(parser, formatter, case):
    before_formatting = drop_comments_and_whitespaces(parser.parse(case.given))
    after_formatting = drop_comments_and_whitespaces(
        parser.parse(formatter.format(case.given))
    )

    assert before_formatting.pretty() == after_formatting.pretty()
    assert before_formatting == after_formatting


pytest_generate_tests = generate_input_output_tests(
    where="formatter/experimental", input_extension=".in", output_extension=".out",
)
