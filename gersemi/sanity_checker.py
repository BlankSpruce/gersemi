from lark import Discard, Tree
from lark.visitors import Transformer
from gersemi.exceptions import ASTMismatch


class DropIrrelevantNodes(Transformer):
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

    def command_element(self, children):
        if len(children) == 1:
            return children[0]
        return Tree("command_element", children)

    def arguments(self, children):
        return Tree("arguments", set(children))

    def _flatten_blocks(self, children):
        for child in children:
            if child.data in ("block", "block_body"):
                yield from child.children
            else:
                yield child

    def file(self, children):
        return Tree("file", list(self._flatten_blocks(children)))

    def block(self, children):
        return Tree("block", list(self._flatten_blocks(children)))

    def block_body(self, children):
        return Tree("block_body", list(self._flatten_blocks(children)))

    NEWLINE = _drop_node
    newline_or_gap = _drop_node


def drop_irrelevant_nodes(tree):
    return DropIrrelevantNodes(visit_tokens=True).transform(tree)


def check_abstract_syntax_trees_equivalence(lhs, rhs):
    plhs = drop_irrelevant_nodes(lhs)
    prhs = drop_irrelevant_nodes(rhs)
    if plhs != prhs:
        raise ASTMismatch


def check_code_equivalence(parser, lhs_parsed, rhs):
    rhs_parsed = parser.parse(rhs)
    check_abstract_syntax_trees_equivalence(lhs_parsed, rhs_parsed)
