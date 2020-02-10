from gersemi.ast_helpers import is_newline
from gersemi.base_dumper import BaseDumper
from gersemi.command_invocation_dumper import CommandInvocationDumper


class Dumper(CommandInvocationDumper, BaseDumper):
    def file(self, tree):
        return "{}\n".format(self.__default__(tree))

    def block(self, tree):
        begin, *middle, end = tree.children
        formatted_middle = "".join(map(self.visit, middle))
        return "{}{}{}".format(self.visit(begin), formatted_middle, self.visit(end))

    def block_body(self, tree):
        result = "".join(self.indented.visit_children(tree))
        if len(result) == 0:
            return "\n"
        return "\n" + result + "\n"

    def command_element(self, tree):
        command_invocation, line_comment = tree.children
        begin = self.visit(command_invocation) + " "
        return self._format_listable_content(begin, line_comment)

    def non_command_element(self, tree):
        non_newline_elements = [
            child for child in tree.children if not is_newline(child)
        ]
        return " ".join(map(self.visit, non_newline_elements))

    def line_comment(self, tree):
        return self._indent("#{}".format("".join(tree.children)))

    def disabled_formatting(self, tree):
        return "\n".join(self.visit_children(tree))

    def disabled_formatting_body(self, tree):
        return "\n".join(tree.children)
