from contextlib import contextmanager
from functools import lru_cache
from gersemi.argument_schema import StandardCommand
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.configuration import OutcomeConfiguration


@lru_cache(maxsize=None)
def create_patch(data, old_class):
    if not isinstance(data, StandardCommand):

        class Impl(data.impl, old_class):  # pylint: disable=function-redefined
            _canonical_name = data.canonical_name

        return Impl

    class Impl(old_class):  # pylint: disable=function-redefined
        _canonical_name = data.canonical_name
        _inhibit_favour_expansion = data.inhibit_favour_expansion
        _two_words_keywords = data.two_words_keywords
        schema = data.schema
        signatures = data.signatures

    return Impl


class Dumper(BaseCommandInvocationDumper):
    def __init__(self, configuration: OutcomeConfiguration, known_definitions):
        self.known_definitions = known_definitions
        super().__init__(configuration)

    @contextmanager
    def patched(self, patch):
        old_class = type(self)
        try:
            self.__class__ = patch
            yield self
        finally:
            self.__class__ = old_class

    def _get_patch(self, raw_command_name):
        command = self.known_definitions.get(raw_command_name.lower(), None)
        if command is None:
            return None

        return create_patch(command, type(self))

    def command_invocation(self, tree):
        command_name, _ = tree.children
        patch = self._get_patch(str(command_name))
        if patch is None:
            return super().format_command(tree)
        with self.patched(patch):
            return self.format_command(tree)

    def custom_command(self, tree):
        _, command_name, *_ = tree.children
        self._record_unknown_command(command_name)
        return super().custom_command(tree)
