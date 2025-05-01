from collections import ChainMap
from itertools import chain
from gersemi.base_dumper import BaseDumper
from gersemi.builtin_commands import _builtin_commands
from gersemi.command_invocation_dumper import CommandInvocationDumper
from gersemi.configuration import OutcomeConfiguration


class Dumper(CommandInvocationDumper, BaseDumper):
    def __init__(self, configuration: OutcomeConfiguration, known_definitions):
        self.known_definitions = ChainMap(known_definitions, _builtin_commands)
        self.list_expansion = configuration.list_expansion
        super().__init__(configuration.line_length, configuration.indent)

    def file(self, tree):
        result = self.__default__(tree)
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
        return self._indent(f"#{''.join(tree.children)}")

    def preformatted_block(self, tree):
        disable_formatter, *body, enable_formatter = tree.children
        return "".join(
            chain(
                [self._indent(disable_formatter)],
                body,
                [self._indent(enable_formatter)],
            )
        )
