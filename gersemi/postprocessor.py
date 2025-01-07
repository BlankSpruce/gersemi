from itertools import dropwhile
from typing import List
from lark import Discard, Tree, Token
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

        if not (is_unquoted_argument(rhs) or is_quoted_argument(rhs)):
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

    def _join_tokens(self, lhs, rhs):
        return Token(
            lhs.children[0].type,
            "".join(lhs.children) + "".join(rhs.children),
            start_pos=lhs.children[0].start_pos,
            end_pos=rhs.children[-1].end_pos,
        )

    def _join_arguments(self, children):
        if len(children) < 2:
            return children

        new_children = []
        previous = children[0]
        for current in children[1:]:
            if not self._valid_pair(previous, current):
                new_children.append(previous)
                previous = current
                continue

            previous = Tree("unquoted_argument", [self._join_tokens(previous, current)])

        new_children.append(previous)
        return new_children

    def arguments(self, children):
        original = children
        new_children = self._join_arguments(children)
        while original != new_children:
            original, new_children = new_children, self._join_arguments(new_children)

        return Tree(
            "arguments", [self._simplify_argument(child) for child in new_children]
        )


class PostProcessor(
    PreserveCustomCommandFormatting,
    SimplifyParseTree,
    RemoveSuperfluousEmptyLines,
    RecognizeUnquotedLegacyArgument,
):
    pass
