from lark import Tree
import pytest
from tests.tests_generator import generate_input_only_tests


def preprocess(node):
    if not isinstance(node, Tree):
        node_type = getattr(node, "type", "ANONYMOUS")
        return f"{node_type} {repr(str(node))}"

    node.children = [preprocess(child) for child in node.children]
    return node


def test_handwritter_parser_vs_lark_based_parser(
    parser_with_postprocessing, handwritten_parser, case
):
    lark_based_parser = parser_with_postprocessing
    lhs = preprocess(lark_based_parser.parse(case.content))
    rhs = preprocess(handwritten_parser.parse(case.content))

    assert lhs.pretty() == rhs.pretty()
    assert lhs == rhs


pytest_generate_tests = generate_input_only_tests(
    where=".",
    input_extension=".cmake",
)
