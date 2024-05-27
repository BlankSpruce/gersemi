from contextlib import contextmanager
from functools import lru_cache
from lark import Tree
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.builtin_commands import BUILTIN_COMMANDS
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
from gersemi.keywords import Keywords


BUILTIN_COMMAND_DUMPERS = {
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


def add_canonical_name(dumper_class, desired_canonical_name):
    class Impl(dumper_class):
        canonical_name = desired_canonical_name

    return Impl


class CommandInvocationDumper(
    PreservingCommandInvocationDumper, BaseCommandInvocationDumper
):
    @contextmanager
    def patched(self, patch):
        old_class = type(self)
        try:
            # pylint: disable=attribute-defined-outside-init
            self.__class__ = create_patch(patch, old_class)
            yield self
        finally:
            self.__class__ = old_class  # pylint: disable=invalid-class-object,

    def _get_patch(self, raw_command_name):
        command_name = raw_command_name.lower()
        if command_name in BUILTIN_COMMANDS:
            canonical_name = BUILTIN_COMMANDS[command_name]

            if command_name in BUILTIN_COMMAND_DUMPERS:
                return add_canonical_name(
                    BUILTIN_COMMAND_DUMPERS[command_name], canonical_name
                )

            return create_specialized_dumper(canonical_name, (), Keywords())

        if command_name in self.custom_command_definitions:
            canonical_name, arguments = self.custom_command_definitions[command_name]
            return create_specialized_dumper(canonical_name, *arguments)

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
        if command_name.lower() in self.custom_command_definitions:
            return self.visit(
                Tree("command_invocation", [command_name.lower(), arguments])
            )
        return super().custom_command(tree)
