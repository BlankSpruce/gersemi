from itertools import chain, repeat
from lark.visitors import Interpreter
from gersemi.ast_helpers import is_space, is_newline


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
                self += "\n"
        elif len(self.lines[-1]) + len(text) > self.width:
            self.lines.append(text)
        else:
            self.lines[-1] += text
        return self

    def __str__(self):
        return "\n".join(
            filter(lambda line: len(line) > 0, map(str.rstrip, self.lines))
        )


def format_comment_content(content, width):
    buffer = WidthLimitingBuffer(width)
    content = " ".join(map(str.lstrip, content.split("\n")))
    first_item, *rest = content.lstrip().split(" ")
    buffer += first_item
    for item in rest:
        buffer += " "
        buffer += item
    return str(buffer)


class DumpToString(Interpreter):
    def __init__(self, width=80):
        super().__init__()
        self.width = width
        self.indent_size = 4

    def __default__(self, tree):
        return "".join(self.visit_children(tree))

    def _format_listable_content(self, anchor, content):
        alignment = len(anchor)
        dumper = DumpToString(self.width - alignment)
        formatted_content = dumper.visit(content)
        buffer = WidthLimitingBuffer(self.width)
        buffer += anchor + indent_except_first_line(formatted_content, alignment)
        return str(buffer)

    def file(self, tree):
        return "{}\n".format(self.__default__(tree))

    def block(self, tree):
        begin, *middle, end = tree.children
        formatted_middle = "\n".join(map(self.visit, middle))
        return "{}\n{}\n{}".format(self.visit(begin), formatted_middle, self.visit(end))

    def block_body(self, tree):
        dumper = DumpToString(self.width - self.indent_size)
        dumped = "".join(dumper.visit_children(tree))
        return indent(dumped, self.indent_size)

    def command_element(self, tree):
        command_invocation, trailing_space, line_comment = tree.children
        begin = self.visit(command_invocation) + self.visit(trailing_space)
        return self._format_listable_content(begin, line_comment)

    def command_invocation(self, tree):
        identifier, left_parenthesis, arguments, right_parenthesis = tree.children

        begin = self.visit(identifier) + left_parenthesis
        result = self._format_listable_content(begin, arguments)

        if "\n" in result:
            result += "\n"
        result += right_parenthesis
        return result

    def arguments(self, tree):
        is_whitespace = lambda node: is_space(node) or is_newline(node)
        only_arguments = [child for child in tree.children if not is_whitespace(child)]
        if len(only_arguments) <= 4:
            result = "".join(self.visit_children(tree))
            if len(result) <= self.width:
                return result

        return "\n".join(self.visit(child) for child in only_arguments)

    def commented_argument(self, tree):
        argument, *_, comment = tree.children
        begin = "".join(self.visit_children(argument)) + " "
        return self._format_listable_content(begin, comment)

    def line_comment(self, tree):
        _, content = tree.children
        comment_start = "# "
        formatted_content = format_comment_content(
            content, self.width - len(comment_start)
        )
        return prefix(formatted_content, repeat(comment_start))

    def bracket_argument(self, tree):
        result = "".join(self.visit_children(tree))
        if len(result) <= self.width:
            return result
        return "\n".join(self.visit_children(tree))

    def bracket_argument_body(self, tree):
        content, *_ = tree.children
        return format_comment_content(content, self.width)
