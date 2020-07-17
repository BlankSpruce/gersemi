from itertools import chain
from gersemi.base_dumper import BaseDumper
from gersemi.command_invocation_dumper import CommandInvocationDumper


class Dumper(CommandInvocationDumper, BaseDumper):
    def __init__(self, width, custom_command_definitions):
        self.custom_command_definitions = custom_command_definitions
        super().__init__(width)

    def file(self, tree):
        result = "{}".format(self.__default__(tree))
        if result.endswith("\n"):
            return result
        return result + "\n"

    def block(self, tree):
        return "\n".join(filter(None, map(self.visit, tree.children)))

    def block_body(self, tree):
        with self.indented():
            return "".join(self.visit_children(tree))

    def command_element(self, tree):
        invocation, *comment = tree.children
        formatted_invocation = self.visit(invocation)
        if len(comment) == 0:
            return formatted_invocation

        with self.not_indented():
            formatted_comment = self.visit(comment[0])

        return f"{formatted_invocation} {formatted_comment}"

    def non_command_element(self, tree):
        return " ".join(self.visit(child) for child in tree.children)

    def line_comment(self, tree):
        return self._indent("#{}".format("".join(tree.children)))

    def preformatted_block(self, tree):
        disable_formatter, *body, enable_formatter = tree.children
        return "".join(
            chain(
                [self._indent(disable_formatter)],
                body,
                [self._indent(enable_formatter)],
            )
        )
