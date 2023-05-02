from contextlib import contextmanager
from textwrap import indent
from typing import Optional
from lark import Tree
from lark.visitors import Interpreter
from gersemi.ast_helpers import contains_line_comment
from gersemi.configuration import ListExpansion
from gersemi.types import Nodes


class BaseDumper(Interpreter):
    def __init__(self, width, alignment=0):
        self.width = width
        self.indent_size = 4
        self.alignment = alignment
        self.favour_expansion = False

    def __default__(self, tree: Tree):
        return "".join(self.visit_children(tree))

    def _indent(self, text: str):
        return indent(text, " " * self.alignment)

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
    def aligned_to(self, alignment):
        old_alignment = self.alignment
        try:
            self.alignment = alignment
            yield self
        finally:
            self.alignment = old_alignment

    def indented(self):
        return self.aligned_to(self.alignment + self.indent_size)

    def not_indented(self):
        return self.aligned_to(0)

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
