from contextlib import contextmanager
from itertools import filterfalse
from typing import Dict, List, Optional, Union
from gersemi.ast_helpers import is_comment, is_unquoted_argument
from gersemi.types import Nodes
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class MultipleSignatureCommandInvocationDumper(ArgumentAwareCommandInvocationDumper):
    customized_signatures: Dict[Optional[str], Dict[str, Union[List, int]]] = {}

    @contextmanager
    def _update_signature_characteristics(self, signature):
        if signature is None:
            yield
            return

        try:

            def get(key):
                return signature.get(key, [])

            self.front_positional_arguments = get("front_positional_arguments")
            self.back_positional_arguments = get("back_positional_arguments")
            self.options = get("options")
            self.one_value_keywords = get("one_value_keywords")
            self.multi_value_keywords = get("multi_value_keywords")
            yield
        finally:
            delattr(self, "front_positional_arguments")
            delattr(self, "back_positional_arguments")
            delattr(self, "options")
            delattr(self, "one_value_keywords")
            delattr(self, "multi_value_keywords")

    def format_command(self, tree):
        _, arguments = tree.children
        arguments = self._preprocess_arguments(arguments)
        arguments_only = filterfalse(is_comment, arguments.children)
        first_argument = next(arguments_only, None)
        if first_argument is None or not is_unquoted_argument(first_argument):
            return super().format_command(tree)
        first_argument_as_value = first_argument.children[0]
        signature = self.customized_signatures.get(first_argument_as_value, None)
        if signature is None:
            signature = self.customized_signatures.get(None, None)

        with self._update_signature_characteristics(signature):
            return super().format_command(tree)

    def _split_arguments(self, arguments: Nodes) -> List[Nodes]:
        signature_node, *rest = arguments
        return [[signature_node], *super()._split_arguments(rest)]
