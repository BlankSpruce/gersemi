from itertools import repeat
from typing import Iterator
from lark import Tree, Token
from lark.visitors import Interpreter
from gersemi.ast_helpers import is_space, is_newline


def prefix(text: str, prefixes: Iterator[str]) -> str:
    lines = []
    for p, line in zip(prefixes, text.split("\n")):
        if line == "":
            lines.append("")
        else:
            lines.append(p + line)
    return "\n".join(lines)


def indent(text: str, width: int) -> str:
    return prefix(text, prefixes=repeat(" " * width))


class WidthLimitingBuffer:
    def __init__(self, width: int):
        self.width = width
        self.lines = [""]

    def __iadd__(self, text: str):
        if text == "\n":
            self.lines.append("")
        elif text == " " and len(self.lines[-1]) == self.width:
            return self
        elif "\n" in text:
            for item in text.split("\n"):
                self += item
                self += "\n"
        elif len(self.lines[-1]) + len(text) > self.width and self.lines[-1] != "":
            self.lines.append(text)
        else:
            self.lines[-1] += text
        return self

    def _remove_ending_newlines(self) -> None:
        while len(self.lines) > 0 and self.lines[-1] == "":
            self.lines.pop()

    def __str__(self) -> str:
        self._remove_ending_newlines()
        return "\n".join(map(str.rstrip, self.lines))


def has_line_comments(node: Token) -> bool:
    class Impl(Interpreter):
        def __default__(self, _) -> bool:
            return False

        def line_comment(self, _) -> bool:
            return True

        def _visit(self, tree: Tree) -> bool:
            is_subtree = lambda node: isinstance(node, Tree)
            subtrees = filter(is_subtree, tree.children)
            return any(map(self.visit, subtrees))

        arguments = _visit
        commented_argument = _visit

    return isinstance(node, Tree) and Impl().visit(node)


class DumpToString(Interpreter):
    def __init__(self, alignment=0):
        super().__init__()
        self.width = 80
        self.indent_size = 4
        self.alignment = alignment

    def __default__(self, tree: Tree):
        return "".join(self.visit_children(tree))

    def _indent(self, text: str):
        return indent(text, self.alignment)

    def _format_listable_content(self, anchor: str, content: str) -> str:
        *_, last_line = anchor.split("\n")
        alignment = len(last_line)
        dumper = type(self)(alignment)
        formatted_content = dumper.visit(content)
        buffer = WidthLimitingBuffer(self.width)
        buffer += anchor + formatted_content.lstrip()
        return str(buffer)

    def _try_to_format_into_single_line(self, tree: Tree):
        dumper = type(self)(alignment=0)
        result = self._indent("".join(dumper.visit_children(tree)))
        if len(result) <= self.width:
            return result
        return None

    def file(self, tree):
        return "{}\n".format(self.__default__(tree))

    def block(self, tree):
        begin, *middle, end = tree.children
        formatted_middle = "".join(map(self.visit, middle))
        return "{}{}{}".format(self.visit(begin), formatted_middle, self.visit(end))

    def block_body(self, tree):
        dumper = type(self)(alignment=self.alignment + self.indent_size)
        result = "".join(dumper.visit_children(tree))
        if len(result) == 0:
            return "\n"
        return "\n" + result + "\n"

    def command_element(self, tree):
        command_invocation, trailing_space, line_comment = tree.children
        begin = self.visit(command_invocation) + self.visit(trailing_space)
        return self._format_listable_content(begin, line_comment)

    def non_command_element(self, tree):
        return self._indent(self.__default__(tree))

    def command_invocation(self, tree):
        identifier, left_parenthesis, arguments, right_parenthesis = tree.children
        begin = self._indent(self.visit(identifier) + left_parenthesis)
        result = self._format_listable_content(begin, arguments)

        if "\n" in result or has_line_comments(arguments):
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

    def bracket_comment(self, tree):
        return " " * self.alignment + self.__default__(tree)

    def bracket_argument(self, tree):
        return " " * self.alignment + self.__default__(tree)

    def quoted_argument(self, tree):
        return " " * self.alignment + self.__default__(tree)

    def unquoted_argument(self, tree):
        return self._indent(self.__default__(tree))
