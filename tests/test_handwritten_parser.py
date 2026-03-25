from gersemi.types import Token
from tests.tests_generator import generate_input_only_tests


def preprocess(node):
    if isinstance(node, (str, Token)):
        node_type = getattr(node, "type", "ANONYMOUS")
        return f"{str(node_type)} {repr(str(node))}"

    return (node.data, [preprocess(child) for child in node.children])


def test_handwritter_parser_vs_lark_based_parser(lark_based_parser, parser, case):
    lhs = preprocess(lark_based_parser.parse(case.content))
    rhs = preprocess(parser.parse(case.content))

    assert lhs == rhs


pytest_generate_tests = generate_input_only_tests(
    where=".",
    input_extension=".cmake",
)
