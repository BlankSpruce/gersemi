from itertools import dropwhile
from typing import List
from lark import Discard, Tree
from lark.visitors import Transformer_InPlace
from gersemi.ast_helpers import is_newline, is_quoted_argument, is_unquoted_argument
from gersemi.builtin_commands import builtin_commands
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
    def non_command_element(self, children: Nodes):
        if len(children) == 0:
            return Discard
        return Tree("non_command_element", children)


class PreserveCustomCommandFormatting(Transformer_InPlace):
    def __init__(self, code):
        super().__init__()
        self.code = code

    def _get_original_formatting(self, lparen, rparen):
        start, end = lparen.end_pos, rparen.start_pos
        content = self.code[start:end]
        return Tree("formatted_node", [content])

    def _get_indentation(self, identifier):
        end = identifier.start_pos
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
        return identifier.lower() in builtin_commands

    def command_invocation(self, children):
        identifier, _, arguments, _ = children
        if self._is_builtin(identifier):
            return Tree("command_invocation", [identifier, arguments])

        return self._make_custom_command(children)


class RecognizeUnquotedLegacyArgument(Transformer_InPlace):
    def _valid_pair(self, lhs, rhs):
        if not is_unquoted_argument(lhs):
            return False

        if not is_quoted_argument(rhs):
            return False

        end = lhs.children[-1].end_pos
        start = rhs.children[0].start_pos
        return end == start

    def _simplify_argument(self, argument):
        if is_quoted_argument(argument):
            if argument.children:
                return Tree("quoted_argument", ["".join(argument.children[1:-1])])
            return Tree("quoted_argument", [])

        return argument

    def arguments(self, children):
        if len(children) < 2:
            return Tree(
                "arguments", [self._simplify_argument(child) for child in children]
            )

        i = 1
        new_children = []
        while i < len(children):
            lhs, rhs = children[i - 1], children[i]

            if not self._valid_pair(lhs, rhs):
                new_children.append(self._simplify_argument(lhs))
                i += 1
                continue

            new_children.append(
                Tree(
                    "unquoted_argument",
                    ["".join(lhs.children) + "".join(rhs.children)],
                )
            )
            i += 2

        if not self._valid_pair(children[-2], children[-1]):
            new_children.append(self._simplify_argument(children[-1]))

        return Tree("arguments", new_children)


class PostProcessor(
    PreserveCustomCommandFormatting,
    SimplifyParseTree,
    RemoveSuperfluousEmptyLines,
    RecognizeUnquotedLegacyArgument,
):
    pass
