from itertools import dropwhile
import os
from typing import List
from lark import Discard, Tree
from lark.visitors import Transformer_InPlace
from gersemi.ast_helpers import is_newline
from gersemi.types import Nodes


class RemoveSuperfluousEmptyLines(Transformer_InPlace):
    def _drop_edge_empty_lines(self, children) -> List:
        while len(children) > 0 and is_newline(children[-1]):
            children.pop()
        return list(dropwhile(is_newline, children))

    def file(self, children) -> Tree:
        return Tree("file", self._drop_edge_empty_lines(children))

    def block_body(self, children) -> Tree:
        return Tree("block_body", self._drop_edge_empty_lines(children))


class SimplifyParseTree(Transformer_InPlace):
    def non_command_element(self, children: Nodes) -> Tree:
        if len(children) == 0:
            raise Discard
        return Tree("non_command_element", children)


def get_builtin_commands():
    HERE = os.path.dirname(os.path.realpath(__file__))
    is_not_comment_or_empty = lambda s: not (s.startswith("#") or len(s) == 0)

    with open(os.path.join(HERE, "builtin_commands"), "r") as f:
        return set(filter(is_not_comment_or_empty, f.read().splitlines()))


class PreserveCustomCommandFormatting(Transformer_InPlace):
    builtin_commands = get_builtin_commands()

    def __init__(self, code):
        super().__init__()
        self.code = code

    def _get_original_formatting(self, lparen, rparen):
        start, end = lparen.end_pos, rparen.pos_in_stream
        content = self.code[start:end]
        return Tree("formatted_node", [content])

    def _get_indentation(self, identifier):
        end = identifier.pos_in_stream
        start = end - identifier.column + 1
        return self.code[start:end]

    def _make_custom_command(self, children):
        identifier, lparen, arguments, rparen = children
        indentation = self._get_indentation(identifier)
        return Tree(
            "custom_command",
            [
                indentation,
                identifier,
                arguments,
                self._get_original_formatting(lparen, rparen),
            ],
        )

    def _is_builtin(self, identifier):
        return identifier in self.builtin_commands

    def command_invocation(self, children):
        identifier, _, arguments, _ = children
        if self._is_builtin(identifier):
            return Tree("command_invocation", [identifier, arguments])

        return self._make_custom_command(children)


class PostProcessor(
    PreserveCustomCommandFormatting, SimplifyParseTree, RemoveSuperfluousEmptyLines
):
    pass
