from itertools import filterfalse
from typing import Dict, List, Union
from gersemi.ast_helpers import is_comment, is_unquoted_argument
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class MultipleSignatureCommandInvocationDumper(ArgumentAwareCommandInvocationDumper):
    customized_signatures: Dict[str, Dict[str, Union[List, int]]] = {}

    def _update_signature_characteristics(self, signature):
        self.options = signature.get("options", [])
        self.one_value_keywords = signature.get("one_value_keywords", [])
        self.multi_value_keywords = signature.get("multi_value_keywords", [])

    def arguments(self, tree):
        arguments_only = filterfalse(is_comment, tree.children)
        first_argument = next(arguments_only, None)
        if first_argument is None or not is_unquoted_argument(first_argument):
            return super().arguments(tree)
        first_argument_as_value = first_argument.children[0]
        signature = self.customized_signatures.get(first_argument_as_value, None)
        if signature is not None:
            self._update_signature_characteristics(signature)
        return super().arguments(tree)
