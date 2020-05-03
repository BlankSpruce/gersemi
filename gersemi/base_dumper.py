from contextlib import contextmanager
from textwrap import indent
from typing import Optional
from lark import Tree
from lark.visitors import Interpreter
from gersemi.types import Nodes
from gersemi.width_limiting_buffer import WidthLimitingBuffer


class BaseDumper(Interpreter):
    def __init__(self, width, alignment=0):
        self.width = width
        self.indent_size = 4
        self.alignment = alignment

    def __default__(self, tree: Tree):
        return "".join(self.visit_children(tree))

    def _format_listable_content(self, anchor: str, content) -> str:
        *_, last_line = anchor.splitlines()
        alignment = len(last_line)
        with self.aligned_to(alignment):
            formatted_content = self.visit(content)
        buffer = WidthLimitingBuffer(self.width)
        buffer += anchor + formatted_content.lstrip()
        return str(buffer)

    def _indent(self, text: str):
        return indent(text, " " * self.alignment)

    def _try_to_format_into_single_line(
        self, children: Nodes, separator: str = "", prefix: str = "", postfix: str = ""
    ) -> Optional[str]:
        with self.not_indented():
            formatted_children = separator.join(map(self.visit, children))
        result = self._indent(f"{prefix}{formatted_children}{postfix}")
        if len(result) <= self.width and "\n" not in result:
            return result
        return None

    def visit(self, tree):
        if isinstance(tree, str):
            return tree
        return super().visit(tree)

    @contextmanager
    def aligned_to(self, alignment):
        try:
            old_alignment = self.alignment
            self.alignment = alignment
            yield self
        finally:
            self.alignment = old_alignment

    def indented(self):
        return self.aligned_to(self.alignment + self.indent_size)

    def not_indented(self):
        return self.aligned_to(0)
