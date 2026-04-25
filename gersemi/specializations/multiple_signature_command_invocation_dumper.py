from contextlib import contextmanager
from itertools import filterfalse
import gersemi_rust_backend
from gersemi.argument_schema import Signatures, create_schema_patch
from gersemi.ast_helpers import is_comment
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

    def _get_signature(self, keyword):
        for item, signature in self.signatures.items():
            if item is None:
                continue

            if gersemi_rust_backend.is_one_of_keywords([item], keyword):
                return signature

        return self.signatures.get(None, None)

    def format_command(self, tree):
        _, arguments = tree.children
        arguments = self._preprocess_arguments(arguments)
        arguments_only = filterfalse(is_comment, arguments.children)
        signature = None
        for argument in arguments_only:
            signature = self._get_signature(argument)
            if signature is not None:
                break

        with self._update_signature_characteristics(signature):
            return super().format_command(tree)
