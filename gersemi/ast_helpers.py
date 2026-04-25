from typing import Any, Callable
from gersemi.interpreter import Interpreter
from gersemi.types import Node, Token, Tree


def is_tree(tree_type: str) -> Callable[[Node], bool]:
    return lambda element: isinstance(element, Tree) and element.data == tree_type


def is_token(token_type: str) -> Callable[[Node], bool]:
    return lambda element: getattr(element, "type", None) == token_type


is_bracket_comment = is_tree("bracket_comment")
is_commented_argument = is_tree("commented_argument")
is_line_comment = is_tree("line_comment")
is_multi_value_argument = is_tree("multi_value_argument")
is_one_value_argument = is_tree("one_value_argument")
is_option_argument = is_tree("option_argument")
is_positional_arguments = is_tree("positional_arguments")
is_quoted_argument = is_tree("quoted_argument")
is_section = is_tree("section")
is_unquoted_argument = is_tree("unquoted_argument")
is_pair = is_tree("pair")

is_newline = is_token("NEWLINE")


def is_comment(element):
    return is_bracket_comment(element) or is_line_comment(element)


class ContainsLineComment(Interpreter):
    def __default__(self, _) -> bool:
        return False

    def line_comment(self, _) -> bool:
        return True

    def _visit(self, tree: Tree) -> bool:
        subtrees = filter(lambda node: isinstance(node, Tree), tree.children)
        return any(map(self.visit, subtrees))

    arguments = _visit
    commented_argument = _visit
    unary_operation = _visit
    binary_operation = _visit


def is_line_comment_in(node) -> bool:
    return ContainsLineComment().visit(node)


def is_line_comment_in_any_of(nodes) -> bool:
    return any(isinstance(node, Tree) and is_line_comment_in(node) for node in nodes)


def is_keyword(keyword, node):
    if not isinstance(node, Tree):
        return False

    if node.data == "commented_argument":
        return node.children and is_keyword(keyword, node.children[0])

    return node.children and node.children[0] == keyword


def get_value(node, default: Any):
    if isinstance(node, (str, Token)):
        return str(node)

    if node.children:
        if is_commented_argument(node):
            return get_value(node.children[0], default)

        if is_quoted_argument(node):
            return node.children[0].value[1:-1]  # type: ignore

        return node.children[0]

    return default
