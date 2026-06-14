from typing import Callable
from gersemi.types import Node, Tree


def is_tree(tree_type: str) -> Callable[[Node], bool]:
    return lambda element: isinstance(element, Tree) and element.data == tree_type


def is_token(token_type: str) -> Callable[[Node], bool]:
    return lambda element: getattr(element, "type", None) == token_type


is_commented_argument = is_tree("commented_argument")
is_quoted_argument = is_tree("quoted_argument")
is_unquoted_argument = is_tree("unquoted_argument")
is_newline = is_token("NEWLINE")
