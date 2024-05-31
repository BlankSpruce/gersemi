from typing import Callable
from lark import Tree, Token
from lark.visitors import Interpreter
from gersemi.types import Node


def is_tree(tree_type: str) -> Callable[[Node], bool]:
    return lambda element: isinstance(element, Tree) and element.data == tree_type


def is_token(token_type: str) -> Callable[[Node], bool]:
    return lambda element: isinstance(element, Token) and element.type == token_type


is_block = is_tree("block")
is_bracket_argument = is_tree("bracket_argument")
is_bracket_comment = is_tree("bracket_comment")
is_commented_argument = is_tree("commented_argument")
is_keyword_argument = is_tree("keyword_argument")
is_line_comment = is_tree("line_comment")
is_multi_value_argument = is_tree("multi_value_argument")
is_one_value_argument = is_tree("one_value_argument")
is_option_argument = is_tree("option_argument")
is_positional_arguments = is_tree("positional_arguments")
is_quoted_argument = is_tree("quoted_argument")
is_section = is_tree("section")
is_two_word_argument = is_tree("two_word_argument")
is_unquoted_argument = is_tree("unquoted_argument")

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


def contains_line_comment(nodes) -> bool:
    visit = ContainsLineComment().visit
    return any(map(lambda node: isinstance(node, Tree) and visit(node), nodes))


def is_keyword(keyword):
    def impl(node):
        if is_unquoted_argument(node):
            return node.children[0] == keyword

        if is_quoted_argument(node):
            return (len(node.children) > 0) and (node.children[0] == keyword)

        if is_bracket_argument(node):
            return (len(node.children) > 0) and (node.children[0] == keyword)

        if is_commented_argument(node):
            return (len(node.children) > 0) and impl(node.children[0])

        return False

    return impl


class KeywordMatcher:
    def __init__(self, keywords):
        self.keywords = keywords

    def __call__(self, other):
        for k in self.keywords:
            if isinstance(k, str):
                if is_keyword(k)(other):
                    return True

            if isinstance(k, tuple) and is_keyword_argument(other):
                front, *_, back = other.children
                front_pattern, back_pattern = k
                if is_keyword(front_pattern)(front) and is_keyword(back_pattern)(back):
                    return True

        return False


def is_one_of_keywords(keywords):
    return KeywordMatcher(keywords)
