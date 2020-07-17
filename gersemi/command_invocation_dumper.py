from contextlib import contextmanager
from lark import Tree
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.command_invocation_dumpers.ctest_command_dumpers import (
    ctest_command_mapping,
)
from gersemi.command_invocation_dumpers.module_command_dumpers import (
    module_command_mapping,
)
from gersemi.command_invocation_dumpers.scripting_command_dumpers import (
    scripting_command_mapping,
)
from gersemi.command_invocation_dumpers.project_command_dumpers import (
    project_command_mapping,
)
from gersemi.command_invocation_dumpers.preserving_command_invocation_dumper import (
    PreservingCommandInvocationDumper,
)


def get_builtin_command_mapping():
    return {
        **scripting_command_mapping,
        **project_command_mapping,
        **ctest_command_mapping,
        **module_command_mapping,
    }


class CommandInvocationDumper(
    PreservingCommandInvocationDumper, BaseCommandInvocationDumper
):
    @contextmanager
    def patched(self, patch):
        old_class = self.__class__

        class Impl(patch, old_class):  # pylint: disable=too-few-public-methods
            pass

        try:
            self.__class__ = Impl
            yield self
        finally:
            self.__class__ = old_class

    def _get_patch(self, command_name):
        return self.known_command_mapping.get(command_name, None)

    def command_invocation(self, tree):
        command_name, _ = tree.children
        patch = self._get_patch(command_name)
        if patch is None:
            return super().format_command(tree)
        with self.patched(patch):
            return self.format_command(tree)

    def custom_command(self, tree):
        _, command_name, arguments, *_ = tree.children
        if command_name in self.known_command_mapping:
            return self.visit(Tree("command_invocation", [command_name, arguments]))
        return super().custom_command(tree)
