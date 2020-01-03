from lark import Discard
from lark.visitors import Transformer
from .tests_generator import generate_input_only_tests


def drop_comments_and_whitespaces(tree):
    class Impl(Transformer):  # pylint: disable=too-few-public-methods
        def _drop_node(self, _):
            raise Discard()

        leading_space = _drop_node
        trailing_space = _drop_node
        non_command_element = _drop_node
        line_comment = _drop_node
        bracket_comment = _drop_node
        SPACE = _drop_node
        NEWLINE = _drop_node

    return Impl(visit_tokens=True).transform(tree)


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
