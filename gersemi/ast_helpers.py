from typing import Callable
from lark import Tree, Token
from lark.visitors import Interpreter
from gersemi.types import Node


def is_tree(tree_type: str) -> Callable[[Node], bool]:
    return lambda element: isinstance(element, Tree) and element.data == tree_type


def is_token(token_type: str) -> Callable[[Node], bool]:
    return lambda element: isinstance(element, Token) and element.type == token_type


is_argument = is_tree("argument")
is_line_comment = is_tree("line_comment")
is_bracket_comment = is_tree("bracket_comment")
is_unquoted_argument = is_tree("unquoted_argument")
is_commented_argument = is_tree("commented_argument")

is_newline = is_token("NEWLINE")

is_comment = lambda element: is_bracket_comment(element) or is_line_comment(element)


def contains_line_comment(nodes) -> bool:
    class Impl(Interpreter):
        def __default__(self, _) -> bool:
            return False

        def line_comment(self, _) -> bool:
            return True

        def _visit(self, tree: Tree) -> bool:
            is_subtree = lambda node: isinstance(node, Tree)
            subtrees = filter(is_subtree, tree.children)
            return any(map(self.visit, subtrees))

        arguments = _visit
        commented_argument = _visit

    check_node = lambda node: isinstance(node, Tree) and Impl().visit(node)
    return any(map(check_node, nodes))


def is_commented_unquoted_argument(node):
    return is_commented_argument(node) and is_unquoted_argument(node.children[0])


def is_keyword(keyword):
    def impl(node):
        return (is_unquoted_argument(node) and node.children[0] == keyword) or (
            is_commented_unquoted_argument(node)
            and node.children[0].children[0] == keyword
        )

    return impl
