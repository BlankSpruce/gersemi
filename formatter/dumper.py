from itertools import chain, repeat
from lark.visitors import Interpreter


def prefix(text, prefixes):
    lines = []
    for p, line in zip(prefixes, text.split("\n")):
        if line == "":
            lines.append("")
        else:
            lines.append(p + line)
    return "\n".join(lines)


def indent(text, width):
    return prefix(text, prefixes=repeat(" " * width))


def indent_except_first_line(text, width):
    return prefix(text, prefixes=chain([""], repeat(" " * width)))


class WidthLimitingBuffer:
    def __init__(self, width):
        self.width = width
        self.lines = [""]

    def __iadd__(self, text):
        if text == "\n":
            self.lines.append("")
        elif text == " " and len(self.lines[-1]) == self.width:
            return self
        elif "\n" in text:
            for item in text.split("\n"):
                self += item
        elif len(self.lines[-1]) + len(text) > self.width:
            self.lines.append(text)
        else:
            self.lines[-1] += text
        return self

    def __str__(self):
        return "\n".join(
            filter(lambda line: len(line) > 0, map(str.rstrip, self.lines))
        )

    @property
    def height(self):
        if len(self.lines) == 1 and self.lines[0] == "":
            return 0
        return len(self.lines)

    @property
    def last_line_used_space(self):
        return len(self.lines[-1])

    def lstrip(self):
        self.lines = [*map(str.lstrip, self.lines)]
        return self


class DumpToString(Interpreter):
    def __init__(self, width=80):
        super().__init__()
        self.width = width
        self.indent_size = 4

    def __default__(self, tree):
        return "".join(self.visit_children(tree))

    def block_body(self, tree):
        dumper = DumpToString(self.width - self.indent_size)
        dumped = "".join(dumper.visit_children(tree))
        return indent(dumped, self.indent_size)

    def command_element(self, tree):
        command_invocation, trailing_space, line_comment = tree.children
        buffer = WidthLimitingBuffer(self.width)
        buffer += self.visit(command_invocation)
        buffer += self.visit(trailing_space)

        alignment = buffer.last_line_used_space
        dumper = DumpToString(self.width - alignment)
        reflowed_line_comment = dumper.visit(line_comment)

        buffer += indent_except_first_line(reflowed_line_comment, width=alignment)
        return str(buffer)

    def command_invocation(self, tree):
        buffer = WidthLimitingBuffer(self.width)
        right_parenthesis = tree.children.pop()
        for child in chain.from_iterable(self.visit_children(tree)):
            buffer += child

        if buffer.height > 1:
            buffer += "\n"
        buffer += right_parenthesis

        return str(buffer.lstrip())

    def arguments(self, tree):
        return self.visit_children(tree)

    def line_comment(self, tree):
        pound_sign, content = tree.children
        comment_start = f"{pound_sign} "
        buffer = WidthLimitingBuffer(self.width - len(comment_start))
        first_item, *rest = content.lstrip().split(" ")
        buffer += first_item
        for item in rest:
            buffer += " "
            buffer += item
        return prefix(str(buffer), repeat(comment_start))
