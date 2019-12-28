from itertools import chain
from lark.visitors import Interpreter


class Indenter:
    @property
    def indent_size(self):
        return 4

    def _indent(self):
        return " " * self.indent_size

    def indent_line(self, line):
        if line == "":
            return ""
        return self._indent() + line

    def indent_text(self, text):
        return "\n".join(map(self.indent_line, text.split("\n")))


class DumpToString(Interpreter):
    def __init__(self, line_limit=80):
        super().__init__()
        self.line_limit = line_limit
        self.indenter = Indenter()

    def __default__(self, tree):
        return "".join(self.visit_children(tree))

    def block_body(self, tree):
        dumper = DumpToString(self.line_limit - self.indenter.indent_size)
        dumped = "".join(dumper.visit_children(tree))
        return self.indenter.indent_text(dumped)

    def command_invocation(self, tree):
        lines = []
        current_line = ""
        children = self.visit_children(tree)
        for child in chain.from_iterable(children):
            if len(current_line) + len(child) > self.line_limit:
                lines.append(current_line.strip())
                current_line = child
            else:
                current_line += child
        lines.append(current_line.strip())
        return "\n".join(filter(lambda line: len(line) > 0, lines))

    def arguments(self, tree):
        return self.visit_children(tree)
