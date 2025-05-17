from contextlib import contextmanager
from itertools import filterfalse
from typing import Dict, List, Optional, Union
from lark import Tree
from gersemi.ast_helpers import is_comment, is_one_of_keywords
from gersemi.keywords import KeywordMatcher
from gersemi.types import Nodes
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)
from .section_aware_command_invocation_dumper import Sections


def create_signature_patch(signature, old_class):
    def get(key, default_value=None):
        return signature.get(key, [] if default_value is None else default_value)

    class Impl(old_class):
        front_positional_arguments = get("front_positional_arguments")
        back_positional_arguments = get("back_positional_arguments")
        options = get("options")
        one_value_keywords = get("one_value_keywords")
        multi_value_keywords = get("multi_value_keywords")
        sections = get("sections", dict())
        keyword_formatters = get("keyword_formatters", dict())
        keyword_preprocessors = get("keyword_preprocessors", dict())

    return Impl


class MultipleSignatureCommandInvocationDumper(ArgumentAwareCommandInvocationDumper):
    signatures: Dict[Optional[KeywordMatcher], Dict[str, Union[List, Sections]]] = {}

    @contextmanager
    def _update_signature_characteristics(self, signature):
        if signature is None:
            yield
            return

        old_class = type(self)
        try:
            self.__class__ = create_signature_patch(signature, old_class)
            yield
        finally:
            self.__class__ = old_class

    def _get_signature_matcher(self, keyword):
        for item in self.signatures:
            matcher = is_one_of_keywords([item])
            if matcher(keyword):
                return item
        return None

    def format_command(self, tree):
        _, arguments = tree.children
        arguments = self._preprocess_arguments(arguments)
        arguments_only = filterfalse(is_comment, arguments.children)
        first_argument = next(arguments_only, None)
        matcher = self._get_signature_matcher(first_argument)

        signature = self.signatures.get(matcher, None)
        with self._update_signature_characteristics(signature):
            return super().format_command(tree)

    def _split_arguments(self, arguments: Nodes) -> Nodes:
        if len(arguments) == 0:
            return []

        signature_node, *rest = arguments
        if isinstance(signature_node, Tree):
            if len(signature_node.children) > 0:
                signature_node_as_value = str(signature_node.children[0])
                if (
                    (signature_node_as_value in self.options)
                    or (signature_node_as_value in self.one_value_keywords)
                    or (signature_node_as_value in self.multi_value_keywords)
                ):
                    return super()._split_arguments(arguments)

        return [
            Tree("positional_arguments", [signature_node]),
            *super()._split_arguments(rest),
        ]
