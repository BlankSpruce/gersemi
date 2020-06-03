from itertools import dropwhile
import os
from typing import Iterator
from lark import Discard, Tree
from lark.visitors import Transformer_InPlace
from gersemi.ast_helpers import is_newline
from gersemi.types import Nodes


class RemoveSuperfluousEmptyLines(Transformer_InPlace):
    def _filter_superfluous_empty_lines(self, children) -> Iterator:
        consecutive_newlines = 0
        for child in children:
            if is_newline(child):
                if consecutive_newlines >= 2:
                    continue
                consecutive_newlines += 1
            else:
                consecutive_newlines = 0
            yield child

    def _drop_edge_empty_lines(self, children) -> Iterator:
        while len(children) > 0 and is_newline(children[-1]):
            children.pop()
        return dropwhile(is_newline, children)

    def _make_node(self, node_type, children) -> Tree:
        new_children = self._filter_superfluous_empty_lines(
            self._drop_edge_empty_lines(children)
        )
        return Tree(node_type, list(new_children))

    def file(self, children) -> Tree:
        return self._make_node("file", children)

    def block_body(self, children) -> Tree:
        return self._make_node("block_body", children)


class SimplifyParseTree(Transformer_InPlace):
    def non_command_element(self, children: Nodes) -> Tree:
        if len(children) == 0:
            raise Discard
        return Tree("non_command_element", children)

    def arguments(self, children: Nodes) -> Tree:
        return Tree("arguments", [child for child in children if not is_newline(child)])


def get_builtin_commands():
    THIS_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(THIS_FILE_DIR, "builtin_commands"), "r") as f:
        return set(f.read().splitlines())


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
