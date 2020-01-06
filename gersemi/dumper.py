from itertools import repeat
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
    def __init__(self, alignment=0):
        super().__init__()
        self.width = 80
        self.indent_size = 4
        self.alignment = alignment

    def __default__(self, tree):
        return "".join(self.visit_children(tree))

    def _indent(self, text):
        return indent(text, self.alignment)

    def _format_listable_content(self, anchor, content):
        *_, last_line = anchor.split("\n")
        alignment = len(last_line)
        dumper = DumpToString(alignment)
        formatted_content = dumper.visit(content)
        buffer = WidthLimitingBuffer(self.width)
        buffer += anchor + formatted_content.lstrip()
        return str(buffer)

    def _try_to_format_into_single_line(self, tree):
        dumper = DumpToString(alignment=0)
        result = self._indent("".join(dumper.visit_children(tree)))
        if len(result) <= self.width:
            return result
        return None

    def file(self, tree):
        return "{}\n".format(self.__default__(tree))

    def block(self, tree):
        begin, *middle, end = tree.children
        formatted_middle = "\n".join(map(self.visit, middle))
        return "{}\n{}\n{}".format(self.visit(begin), formatted_middle, self.visit(end))

    def block_body(self, tree):
        dumper = DumpToString(alignment=self.alignment + self.indent_size)
        return "".join(dumper.visit_children(tree))

    def command_element(self, tree):
        command_invocation, trailing_space, line_comment = tree.children
        begin = self.visit(command_invocation) + self.visit(trailing_space)
        return self._format_listable_content(begin, line_comment)

    def command_invocation(self, tree):
        identifier, left_parenthesis, arguments, right_parenthesis = tree.children
        begin = self._indent(self.visit(identifier) + left_parenthesis)
        result = self._format_listable_content(begin, arguments)

        if "\n" in result:
            result += "\n" + self._indent(right_parenthesis)
        else:
            result += right_parenthesis
        return result

    def arguments(self, tree):
        is_whitespace = lambda node: is_space(node) or is_newline(node)
        only_arguments = [child for child in tree.children if not is_whitespace(child)]
        if len(only_arguments) <= 4:
            result = self._try_to_format_into_single_line(tree)
            if result is not None:
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
            content, self.width - self.alignment - len(comment_start)
        )
        return self._indent(prefix(formatted_content, repeat(comment_start)))

    def bracket_comment(self, tree):
        result = self._try_to_format_into_single_line(tree)
        if result is not None:
            return result
        return self._indent("\n".join(self.visit_children(tree)))

    def bracket_comment_body(self, tree):
        content, *_ = tree.children
        return format_comment_content(content, self.width - self.alignment)

    def bracket_argument(self, tree):
        return " " * self.alignment + self.__default__(tree)

    def quoted_argument(self, tree):
        return " " * self.alignment + self.__default__(tree)

    def unquoted_argument(self, tree):
        return self._indent(self.__default__(tree))
