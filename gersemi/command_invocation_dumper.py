from contextlib import contextmanager
from functools import lru_cache
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
from gersemi.command_invocation_dumpers.specialized_dumpers import (
    create_specialized_dumper,
)

BUILTIN_COMMAND_MAPPING = {
    **scripting_command_mapping,
    **project_command_mapping,
    **ctest_command_mapping,
    **module_command_mapping,
}


@lru_cache(maxsize=None)
def create_patch(patch, old_class):
    class Impl(patch, old_class):
        pass

    return Impl


class CommandInvocationDumper(
    PreservingCommandInvocationDumper, BaseCommandInvocationDumper
):
    @contextmanager
    def patched(self, patch):
        old_class = self.__class__
        try:
            self.__class__ = create_patch(patch, old_class)
            yield self
        finally:
            self.__class__ = old_class

    def _get_patch(self, command_name):
        if command_name in BUILTIN_COMMAND_MAPPING:
            return BUILTIN_COMMAND_MAPPING[command_name]

        if command_name in self.custom_command_definitions:
            keywords = self.custom_command_definitions[command_name]
            return create_specialized_dumper(keywords)

        return None

    def command_invocation(self, tree):
        command_name, _ = tree.children
        patch = self._get_patch(command_name)
        if patch is None:
            return super().format_command(tree)
        with self.patched(patch):
            return self.format_command(tree)

    def custom_command(self, tree):
        _, command_name, arguments, *_ = tree.children
        if command_name in self.custom_command_definitions:
            return self.visit(Tree("command_invocation", [command_name, arguments]))
        return super().custom_command(tree)
