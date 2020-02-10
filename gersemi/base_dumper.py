from typing import Optional
from lark import Tree
from lark.visitors import Interpreter
from gersemi.indenter import indent
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
        dumper = type(self)(self.width, alignment)
        formatted_content = dumper.visit(content)
        buffer = WidthLimitingBuffer(self.width)
        buffer += anchor + formatted_content.lstrip()
        return str(buffer)

    def _indent(self, text: str):
        return indent(text, self.alignment)

    def _try_to_format_into_single_line(
        self, children: Nodes, separator: str = "", prefix: str = "", postfix: str = ""
    ) -> Optional[str]:
        result = self._indent(
            prefix
            + separator.join(map(self.with_no_indentation.visit, children))
            + postfix
        )
        if len(result) <= self.width and "\n" not in result:
            return result
        return None

    def visit(self, tree):
        if isinstance(tree, str):
            return tree
        return super().visit(tree)

    @property
    def indented(self):
        return type(self)(self.width, self.alignment + self.indent_size)

    @property
    def with_no_indentation(self):
        return type(self)(self.width, 0)
