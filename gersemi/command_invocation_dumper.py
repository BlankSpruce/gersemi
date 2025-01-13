import collections.abc
from contextlib import contextmanager
from functools import lru_cache
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.specializations.preserving_command_invocation_dumper import (
    PreservingCommandInvocationDumper,
)
from gersemi.specializations.standard_command_dumper import (
    create_standard_dumper,
)


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
        old_class = type(self)
        try:
            # pylint: disable=attribute-defined-outside-init
            self.__class__ = create_patch(patch, old_class)
            yield self
        finally:
            self.__class__ = old_class  # pylint: disable=invalid-class-object,

    def _get_patch(self, raw_command_name):
        command = self.known_definitions.get(raw_command_name.lower(), None)
        if isinstance(command, collections.abc.Mapping):
            return create_standard_dumper(command)

        return command

    def command_invocation(self, tree):
        command_name, _ = tree.children
        patch = self._get_patch(command_name)
        if patch is None:
            return super().format_command(tree)
        with self.patched(patch):
            return self.format_command(tree)

    def custom_command(self, tree):
        _, command_name, *_ = tree.children
        self._record_unknown_command(command_name)
        return super().custom_command(tree)
