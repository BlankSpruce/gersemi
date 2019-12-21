from itertools import filterfalse
from lark import Tree, Token
from lark.visitors import Transformer_InPlace


def convert_to_string(tree):
    result = ""
    for child in tree.children:
        if type(child) is Token:
            result += str(child)
        else:
            result += convert_to_string(child)
    return result


def is_space(element):
    return type(element) is Token and element.type == 'SPACE'


def remove_if_space(children, index):
    if len(children) > 0 and is_space(children[index]):
        children.pop(index)


def is_space_at_line_beginning(element):
    return is_space(element) and element.column == 1


class RemoveSuperfluousSpaces(Transformer_InPlace):
    def file_element(self, children):
        remove_if_space(children, index=0)
        remove_if_space(children, index=-1)
        return Tree('file_element', children)

    def command_invocation(self, children):
        remove_if_space(children, index=0)
        remove_if_space(children, index=1)
        return Tree('command_invocation', children)

    def arguments(self, children):
        remove_if_space(children, index=0)
        remove_if_space(children, index=-1)
        children = [*filterfalse(is_space_at_line_beginning, children)]

        return Tree('arguments', children)


class ReduceSpacesToOneCharacter(Transformer_InPlace):
    def SPACE(self, ignored):
        return Token('SPACE', ' ')


class Formatter:
    def __init__(self, parser):
        self.parser = parser

    def format(self, code):
        transformer = RemoveSuperfluousSpaces() * ReduceSpacesToOneCharacter(visit_tokens=True)
        return convert_to_string(
            transformer.transform(
                self.parser.parse(code)
            )
        )


def create_formatter(parser):
    return Formatter(parser)
