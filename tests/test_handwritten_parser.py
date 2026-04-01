from gersemi.types import Token, Tree
import gersemi_rust_parser
from tests.tests_generator import generate_input_only_tests


def preprocess(node, dbg_types=False):
    if isinstance(node, gersemi_rust_parser.Node.Token):
        if dbg_types:
            node_type = getattr(node, "type_", "ANONYMOUS")
            return f"{str(node_type)} {repr(node.value)}"

        return repr(node.value)

    if isinstance(node, (str, Token)):
        if dbg_types:
            node_type = getattr(node, "type", "ANONYMOUS")
            return f"{str(node_type)} {repr(str(node))}"

        return repr(str(node))

    return (node.data, [preprocess(child, dbg_types) for child in node.children])


def test_handwritter_parser_vs_lark_based_parser(lark_based_parser, parser, case):
    lhs = preprocess(lark_based_parser.parse(case.content))
    rhs = preprocess(parser.parse(case.content))

    assert lhs == rhs


def test_handwritten_parser_vs_rust_parser(parser, rust_parser, case):
    lhs = preprocess(parser.parse(case.content))
    rhs = preprocess(rust_parser.parse(case.content))

    assert lhs == rhs


pytest_generate_tests = generate_input_only_tests(
    where=".",
    input_extension=".cmake",
)
