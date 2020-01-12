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
