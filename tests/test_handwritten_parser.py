from lark import Tree
import pytest
from tests.tests_generator import generate_input_only_tests
from tests.wip.handwritten_parser import parse as handwritten_parser


def preprocess(node):
    if not isinstance(node, Tree):
        return f"{node.type} {repr(str(node))}"

    node.children = [preprocess(child) for child in node.children]
    return node


def test_handwritter_parser_vs_lark_based_parser(parser, case):
    if case.name in (
        "executable/utf-8-bom/expected",
        "executable/utf-8-bom/given",
    ):
        pytest.skip("Unsupported")

    lhs = preprocess(parser.parse(case.content))
    rhs = preprocess(handwritten_parser(case.content))

    assert lhs.pretty() == rhs.pretty()
    assert lhs == rhs


pytest_generate_tests = generate_input_only_tests(
    where=".",
    input_extension=".cmake",
)
