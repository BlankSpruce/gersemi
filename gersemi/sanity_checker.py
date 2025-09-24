from lark import Discard, Tree
from gersemi.ast_helpers import is_newline
from gersemi.exceptions import ASTMismatch
from gersemi.transformer import Transformer_InPlace


def is_not_newline(node):
    return not is_newline(node)


def remove_newlines(nodes):
    yield from filter(is_not_newline, nodes)


class DropIrrelevantNodes(Transformer_InPlace):
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

    def commented_argument(self, children):
        return Tree("commented_argument", list(remove_newlines(children)))

    def non_command_element(self, children):
        if len(children) == 0:
            return Discard
        return Tree("non_command_element", children)

    def command_element(self, children):
        if len(children) == 1:
            return children[0]
        return Tree("command_element", children)

    def arguments(self, children):
        return Tree("arguments", set(remove_newlines(children)))

    def _flatten_blocks(self, children):
        for child in children:
            if getattr(child, "data", None) in ("block", "block_body"):
                yield from child.children
            else:
                yield child

    def start(self, children):
        return Tree("start", list(remove_newlines(self._flatten_blocks(children))))

    def block(self, children):
        return Tree("block", list(remove_newlines(self._flatten_blocks(children))))

    def block_body(self, children):
        return Tree("block_body", list(remove_newlines(self._flatten_blocks(children))))

    newline_or_gap = _drop_node


def drop_irrelevant_nodes(tree):
    return DropIrrelevantNodes().transform(tree)


def check_abstract_syntax_trees_equivalence(lhs, rhs):
    plhs = drop_irrelevant_nodes(lhs)
    prhs = drop_irrelevant_nodes(rhs)
    if plhs != prhs:
        raise ASTMismatch


def check_code_equivalence(parser, lhs_parsed, rhs):
    rhs_parsed = parser.parse(rhs)
    check_abstract_syntax_trees_equivalence(lhs_parsed, rhs_parsed)
