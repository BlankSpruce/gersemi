from lark import Discard, Tree
from lark.visitors import Transformer
from gersemi.exceptions import ASTMismatch


class DropWhitespaces(Transformer):
    def _drop_node(self, _):
        raise Discard()

    def non_command_element(self, children):
        if len(children) == 0:
            raise Discard()
        return Tree("non_command_element", children)

    NEWLINE = _drop_node
    newline_or_gap = _drop_node


def drop_whitespaces(tree):
    return DropWhitespaces(visit_tokens=True).transform(tree)


def check_abstract_syntax_trees_equivalence(lhs, rhs):
    preprocess = drop_whitespaces
    if preprocess(lhs) != preprocess(rhs):
        raise ASTMismatch


def check_code_equivalence(parser, lhs, rhs):
    lhs_parsed, rhs_parsed = parser.parse(lhs), parser.parse(rhs)
    check_abstract_syntax_trees_equivalence(lhs_parsed, rhs_parsed)
