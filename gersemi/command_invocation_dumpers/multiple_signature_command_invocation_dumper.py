from typing import Dict, List, Optional, Union
from lark import Tree
from lark.visitors import Interpreter
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


def unquoted_argument_to_value(argument) -> Optional[str]:
    class Impl(Interpreter):
        def __default__(self, tree: Tree):
            return None

        def argument(self, tree: Tree):
            return self.visit(tree.children[0])

        def _join_children(self, tree):
            return "".join(self.visit_children(tree))

        unquoted_argument = _join_children
        unquoted_element = _join_children
        make_style_reference = _join_children
        double_quoted_string = _join_children

    if isinstance(argument, Tree):
        return Impl().visit(argument)
    return None


class MultipleSignatureCommandInvocationDumper(ArgumentAwareCommandInvocationDumper):
    customized_signatures: Dict[str, Dict[str, Union[List, int]]] = {}

    def _update_signature_characteristics(self, signature):
        self.options = signature.get("options", [])
        self.one_value_keywords = signature.get("one_value_keywords", [])
        self.multi_value_keywords = signature.get("multi_value_keywords", [])

    def arguments(self, tree):
        first_argument, *_ = tree.children
        first_argument_as_value = unquoted_argument_to_value(first_argument)
        signature = self.customized_signatures.get(first_argument_as_value, None)
        if signature is not None:
            self._update_signature_characteristics(signature)
        return super().arguments(tree)
