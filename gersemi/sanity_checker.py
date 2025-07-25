from lark import Discard, Tree
from lark.visitors import Transformer
from gersemi.exceptions import ASTMismatch


class DropWhitespaces(Transformer):
    def _drop_node(self, _):
        return Discard

    def line_comment(self, children):
        if not children:
            return Tree("line_comment", [])

        comment_content, *_ = children
        return Tree("line_comment", [comment_content.rstrip()])

    def command_invocation(self, children):
        command_name, *rest = children
        return Tree("command_invocation", [command_name.lower(), *rest])

    def non_command_element(self, children):
        if len(children) == 0:
            return Discard
        return Tree("non_command_element", children)

    def arguments(self, children):
        return Tree("arguments", set(children))

    NEWLINE = _drop_node
    newline_or_gap = _drop_node


def drop_whitespaces(tree):
    return DropWhitespaces(visit_tokens=True).transform(tree)


def check_abstract_syntax_trees_equivalence(lhs, rhs):
    preprocess = drop_whitespaces
    if preprocess(lhs) != preprocess(rhs):
        raise ASTMismatch


def check_code_equivalence(parser, lhs_parsed, rhs):
    rhs_parsed = parser.parse(rhs)
    check_abstract_syntax_trees_equivalence(lhs_parsed, rhs_parsed)
