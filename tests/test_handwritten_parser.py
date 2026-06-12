import gersemi_rust_backend
from gersemi.types import Token
from tests.tests_generator import generate_input_only_tests


def preprocess(node, dbg_types=False):
    if isinstance(node, (str, Token)):
        if dbg_types:
            node_type = getattr(node, "type", "ANONYMOUS")
            return f"{str(node_type)} {repr(str(node))}"

        return repr(str(node))

    return (node.data, [preprocess(child, dbg_types) for child in node.children])


def test_rust_parser_vs_lark_based_parser(lark_based_parser, rust_parser, case):
    lhs = preprocess(lark_based_parser.parse(case.content))
    rhs = preprocess(rust_parser.parse(case.content))

    assert lhs == rhs


def test_rust_type_conversion_back_and_forth(rust_parser, case):
    parsed = rust_parser.parse(case.content)
    converted_back_and_forth = gersemi_rust_backend.convert_node(parsed)

    assert preprocess(parsed) == preprocess(converted_back_and_forth)


pytest_generate_tests = generate_input_only_tests(
    where=".",
    input_extension=".cmake",
)
