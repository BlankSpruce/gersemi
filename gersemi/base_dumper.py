from contextlib import contextmanager
from textwrap import indent
from typing import Optional
from lark import Tree
from lark.visitors import Interpreter
from gersemi.ast_helpers import contains_line_comment
from gersemi.configuration import Indent, ListExpansion, Tabs
from gersemi.types import Nodes


def get_indent(indent_type: Indent) -> str:
    if isinstance(indent_type, Tabs):
        return "\t"
    return " " * indent_type


class BaseDumper(Interpreter):
    def __init__(self, width, indent_type):
        self.width = width
        self.indent_type = indent_type
        self._indent_symbol = get_indent(self.indent_type)
        self.indent_level = 0
        self.favour_expansion = False

    def __default__(self, tree: Tree):
        return "".join(self.visit_children(tree))

    @property
    def indent_symbol(self):
        return self._indent_symbol * self.indent_level

    def _indent(self, text: str):
        return indent(text, self.indent_symbol)

    def _try_to_format_into_single_line(
        self, children: Nodes, separator: str = "", prefix: str = "", postfix: str = ""
    ) -> Optional[str]:
        if self.favour_expansion:
            return None

        if not contains_line_comment(children):
            with self.not_indented():
                formatted_children = separator.join(
                    self.visit(c) if isinstance(c, Tree) else c for c in children
                )
            result = self._indent(f"{prefix}{formatted_children}{postfix}")
            if len(result) <= self.width and "\n" not in result:
                return result
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
