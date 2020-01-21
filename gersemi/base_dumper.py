from typing import Optional
from lark import Tree
from lark.visitors import Interpreter
from gersemi.indenter import indent
from gersemi.types import Nodes
from gersemi.width_limiting_buffer import WidthLimitingBuffer


class BaseDumper(Interpreter):
    def __init__(self, alignment=0):
        self.width = 80
        self.indent_size = 4
        self.alignment = alignment

    def __default__(self, tree: Tree):
        return "".join(self.visit_children(tree))

    def _format_listable_content(self, anchor: str, content) -> str:
        *_, last_line = anchor.splitlines()
        alignment = len(last_line)
        dumper = type(self)(alignment)
        formatted_content = dumper.visit(content)
        buffer = WidthLimitingBuffer(self.width)
        buffer += anchor + formatted_content.lstrip()
        return str(buffer)

    def _indent(self, text: str):
        return indent(text, self.alignment)

    def _try_to_format_into_single_line(
        self, children: Nodes, separator=""
    ) -> Optional[str]:
        dumper = type(self)(alignment=0)
        result = self._indent(separator.join(map(dumper.visit, children)))
        if len(result) <= self.width:
            return result
        return None

    def visit(self, tree):
        if isinstance(tree, str):
            return tree
        return super().visit(tree)