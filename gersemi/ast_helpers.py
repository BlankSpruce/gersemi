from typing import Callable
from lark import Tree, Token
from lark.visitors import Interpreter
from gersemi.types import Node


def is_tree(tree_type: str) -> Callable[[Node], bool]:
    return lambda element: isinstance(element, Tree) and element.data == tree_type


def is_token(token_type: str) -> Callable[[Node], bool]:
    return lambda element: isinstance(element, Token) and element.type == token_type


is_line_comment = is_tree("line_comment")
is_bracket_comment = is_tree("bracket_comment")
is_unquoted_argument = is_tree("unquoted_argument")
is_commented_argument = is_tree("commented_argument")
is_block = is_tree("block")

is_newline = is_token("NEWLINE")

is_comment = lambda element: is_bracket_comment(element) or is_line_comment(element)


class ContainsLineComment(Interpreter):
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


def contains_line_comment(nodes) -> bool:
    visit = ContainsLineComment().visit
    check_node = lambda node: isinstance(node, Tree) and visit(node)
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


class KeywordMatcher:
    def __init__(self, keywords):
        self.keywords = keywords

    def __eq__(self, other):
        return any(map(other.__eq__, self.keywords))


def is_one_of_keywords(keywords):
    return is_keyword(KeywordMatcher(keywords))
