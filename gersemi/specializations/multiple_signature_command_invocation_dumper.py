from contextlib import contextmanager
from itertools import filterfalse
from gersemi.argument_schema import Signatures, create_schema_patch
from gersemi.ast_helpers import is_comment, is_one_of_keywords
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class MultipleSignatureCommandInvocationDumper(ArgumentAwareCommandInvocationDumper):
    signatures: Signatures = {}

    @contextmanager
    def _update_signature_characteristics(self, signature):
        if signature is None:
            yield
            return

        old_class = type(self)
        try:
            self.__class__ = create_schema_patch(signature, old_class)
            yield
        finally:
            self.__class__ = old_class

    def _get_signature_matcher(self, keyword):
        for item in self.signatures:
            if is_one_of_keywords([item], keyword):
                return item
        return None

    def format_command(self, tree):
        _, arguments = tree.children
        arguments = self._preprocess_arguments(arguments)
        arguments_only = filterfalse(is_comment, arguments.children)
        matcher = None
        for argument in arguments_only:
            matcher = self._get_signature_matcher(argument)
            if matcher is not None:
                break

        signature = self.signatures.get(matcher, None)
        with self._update_signature_characteristics(signature):
            return super().format_command(tree)
