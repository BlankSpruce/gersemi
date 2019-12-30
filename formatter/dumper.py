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


class WidthLimitingBuffer:
    def __init__(self, width):
        self.width = width
        self.lines = [""]

    def __iadd__(self, text):
        if self.lines[-1] == "":
            self.lines[-1] += text.lstrip()
        elif text == "\n":
            self.lines.append("")
        elif len(self.lines[-1]) + len(text) > self.width:
            self.lines.append(text.lstrip())
        else:
            self.lines[-1] += text
        return self

    def __str__(self):
        return "\n".join(filter(lambda line: len(line) > 0, map(str.strip, self.lines)))

    @property
    def height(self):
        if len(self.lines) == 1 and self.lines[0] == "":
            return 0
        return len(self.lines)

    @property
    def last_line_used_space(self):
        return len(self.lines[-1])


def prefix_each_line(text, prefix):
    return prefix + ("\n" + prefix).join(text.split("\n"))


class DumpToString(Interpreter):
    def __init__(self, width=80):
        super().__init__()
        self.width = width
        self.indenter = Indenter()

    def __default__(self, tree):
        return "".join(self.visit_children(tree))

    def block_body(self, tree):
        dumper = DumpToString(self.width - self.indenter.indent_size)
        dumped = "".join(dumper.visit_children(tree))
        return self.indenter.indent_text(dumped)

    def command_element(self, tree):
        command_invocation, trailing_space, line_comment = tree.children
        buffer = WidthLimitingBuffer(self.width)
        buffer += self.visit(command_invocation)
        buffer += self.visit(trailing_space)

        alignment = buffer.last_line_used_space
        dumper = DumpToString(self.width - alignment)
        reflowed_line_comment = dumper.visit(line_comment)

        first_line, *rest = reflowed_line_comment.split("\n", maxsplit=1)
        buffer += first_line
        result = str(buffer)
        if len(rest) > 0:
            result += "\n"
            result += prefix_each_line(rest[0], prefix=" " * alignment)
        return result

    def command_invocation(self, tree):
        buffer = WidthLimitingBuffer(self.width)
        right_parenthesis = tree.children.pop()
        for child in chain.from_iterable(self.visit_children(tree)):
            buffer += child

        if buffer.height > 1:
            buffer += "\n"
        buffer += right_parenthesis

        return str(buffer)

    def arguments(self, tree):
        return self.visit_children(tree)

    def line_comment(self, tree):
        pound_sign, content = tree.children
        prefix = f"{pound_sign} "
        buffer = WidthLimitingBuffer(self.width - len(prefix))
        first_item, *rest = content.split(" ")
        buffer += first_item
        for item in rest:
            buffer += " "
            buffer += item
        return prefix_each_line(str(buffer), prefix)
