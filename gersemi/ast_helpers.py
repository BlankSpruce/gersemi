from lark import Tree, Token


def is_tree(tree_type):
    return lambda element: isinstance(element, Tree) and element.data == tree_type


def is_token(token_type):
    return lambda element: isinstance(element, Token) and element.type == token_type


is_argument = is_tree("argument")
is_line_comment = is_tree("line_comment")
is_bracket_comment = is_tree("bracket_comment")

is_space = is_token("SPACE")
is_newline = is_token("NEWLINE")

is_comment = lambda element: is_bracket_comment(element) or is_line_comment(element)
