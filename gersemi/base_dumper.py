from collections import defaultdict
from contextlib import contextmanager
from textwrap import indent
from typing import Optional
from lark import Tree
from lark.visitors import Interpreter
from gersemi.ast_helpers import is_line_comment_in
from gersemi.configuration import Indent, ListExpansion, Tabs
from gersemi.types import Nodes
from gersemi.warnings import FormatterWarnings, UnknownCommandWarning


def get_indent(indent_type: Indent) -> str:
    if isinstance(indent_type, Tabs):
        return "\t"
    return " " * indent_type


class WontFit(Exception):
    pass


class BaseDumper(Interpreter):
    def __init__(self, width, indent_type):
        self.width = width
        self.indent_type = indent_type
        self._indent_symbol = get_indent(self.indent_type)
        self.indent_level = 0
        self.favour_expansion = False
        self.unknown_commands_used = defaultdict(list)

    def __default__(self, tree: Tree):
        return "".join(self.visit_children(tree))

    @property
    def indent_symbol(self):
        return self._indent_symbol * self.indent_level

    def _indent(self, text: str):
        return indent(text, self.indent_symbol)

    def _single_line_helper(self, children, offset):
        width = offset
        for c in children:
            if isinstance(c, Tree):
                if is_line_comment_in(c):
                    raise WontFit()

                result = self.visit(c)
            else:
                result = c

            if "\n" in result:
                raise WontFit()

            width += len(result)
            if width > self.width:
                raise WontFit()

            yield result
            width += 1

    def _try_to_format_into_single_line(
        self, children: Nodes, prefix: str = "", postfix: str = ""
    ) -> Optional[str]:
        if self.favour_expansion:
            return None

        try:
            reserved_space = len(prefix) + len(postfix) + len(self.indent_symbol)
            with self.not_indented():
                formatted = " ".join(self._single_line_helper(children, reserved_space))
            return f"{self.indent_symbol}{prefix}{formatted}{postfix}"
        except WontFit:
            return None

    @contextmanager
    def with_indent_level(self, indent_level):
        old_indent_level = self.indent_level
        try:
            self.indent_level = indent_level
            yield self
        finally:
            self.indent_level = old_indent_level

    def indented(self):
        return self.with_indent_level(self.indent_level + 1)

    def not_indented(self):
        return self.with_indent_level(0)

    @contextmanager
    def select_expansion_strategy(self):
        old = self.favour_expansion
        try:
            self.favour_expansion = self.list_expansion == ListExpansion.FavourExpansion
            yield self
        finally:
            self.favour_expansion = old

    @contextmanager
    def select_inlining_strategy(self):
        old = self.favour_expansion
        try:
            self.favour_expansion = False
            yield self
        finally:
            self.favour_expansion = old

    def format_command_name(self, identifier):
        return identifier.lower()

    def _record_unknown_command(self, command):
        self.unknown_commands_used[str(command)].append((command.line, command.column))

    def get_warnings(self) -> FormatterWarnings:
        if len(self.unknown_commands_used) == 0:
            return []

        return [
            UnknownCommandWarning(command_name=name, positions=positions)
            for name, positions in self.unknown_commands_used.items()
        ]
