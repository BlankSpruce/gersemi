from functools import reduce
from itertools import filterfalse
from lark import Tree, Token
from lark.visitors import Transformer_InPlace, Interpreter

from formatter.dumper import DumpToString


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

    def command_element(self, children):
        if len(children) > 2:
            remove_if_space(children, index=2)
        children.pop(0)
        return Tree('command_element', children)

    def non_command_element(self, children):
        remove_if_space(children, index=0)
        return Tree('non_command_element', children)

    def command_invocation(self, children):
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


def is_command(command_name):
    class IsCommandImpl(Interpreter):
        def command_element(self, tree):
            _, command_invocation, *_ = tree.children
            return self.visit(command_invocation)

        def command_invocation(self, tree):
            identifier, *_ = tree.children
            return self.visit(identifier)

        def identifier(self, tree):
            name, *_ = tree.children
            return name == command_name

        def __default__(self, *args):
            return False

    return lambda node: type(node) == Tree and IsCommandImpl().visit(node)


is_if = is_command('if')
is_endif = is_command('endif')


class IsolateIfBlocks(Transformer_InPlace):
    def _restructure(self, node_stream, begin=None):
        children = []
        for node in node_stream:
            if is_if(node):
                children.append(self._restructure(node_stream, begin=node))
            elif is_endif(node):
                return Tree('block', [
                    Tree('block_begin', begin.children),
                    Tree('block_body', children),
                    Tree('block_end', node.children),
                ])
            else:
                children.append(node)
        return children

    def file(self, children):
        children_as_stream = (child for child in children)
        return Tree('file', self._restructure(children_as_stream))


def compose_transformers(*transformers):
    return reduce(lambda a, b: a * b, transformers)


class Formatter:
    def __init__(self, parser):
        self.parser = parser

    def format(self, code):
        transformer = compose_transformers(
            IsolateIfBlocks(),
            RemoveSuperfluousSpaces(),
            ReduceSpacesToOneCharacter(visit_tokens=True),
            DumpToString()
        )
        return transformer.transform(self.parser.parse(code))


def create_formatter(parser):
    return Formatter(parser)
