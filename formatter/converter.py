from lark import Token


def convert_to_string(tree):
    result = ""
    for child in tree.children:
        if type(child) is Token:
            result += str(child)
        else:
            result += convert_to_string(child)
    return result
