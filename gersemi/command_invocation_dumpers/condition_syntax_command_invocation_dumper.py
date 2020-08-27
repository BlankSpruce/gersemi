from typing import List
from lark import Tree
from lark.visitors import Transformer, TransformerChain, Transformer_InPlace
from gersemi.ast_helpers import contains_line_comment, is_one_of_keywords
from gersemi.types import Nodes
from gersemi.utils import advance
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class IsolateUnaryOperators(Transformer_InPlace):
    unary_operators: List[str] = []

    def arguments(self, children: Nodes) -> Tree:
        if len(children) < 2:
            return Tree("arguments", children)

        new_children: Nodes = []
        iterator = zip(children, children[1:])
        is_one_of_unary_operators = is_one_of_keywords(self.unary_operators)
        for one_behind, current in iterator:
            if is_one_of_unary_operators(one_behind):
                new_children += [Tree("unary_operation", [one_behind, current])]
                _, current = advance(iterator, times=1, default=(None, None))
                if current is None:
                    break
            else:
                new_children += [one_behind]
        else:
            new_children += [item for item in [current] if item is not None]
        return Tree("arguments", new_children)


class IsolateUnaryTests(IsolateUnaryOperators):
    unary_operators: List[str] = [
        "COMMAND",
        "POLICY",
        "TARGET",
        "TEST",
        "EXISTS",
        "IS_DIRECTORY",
        "IS_SYMLINK",
        "IS_ABSOLUTE",
        "DEFINED",
    ]


class IsolateBinaryTests(Transformer_InPlace):
    binary_operators: List[str] = [
        "IS_NEWER_THAN",
        "MATCHES",
        "LESS",
        "GREATER",
        "EQUAL",
        "LESS_EQUAL",
        "GREATER_EQUAL",
        "STRLESS",
        "STRGREATER",
        "STREQUAL",
        "STRLESS_EQUAL",
        "STRGREATER_EQUAL",
        "VERSION_LESS",
        "VERSION_GREATER",
        "VERSION_EQUAL",
        "VERSION_LESS_EQUAL",
        "VERSION_GREATER_EQUAL",
        "IN_LIST",
    ]

    def arguments(self, children: Nodes) -> Tree:
        if len(children) < 3:
            return Tree("arguments", children)

        new_children: Nodes = []
        iterator = zip(children, children[1:], children[2:])
        is_one_of_binary_operators = is_one_of_keywords(self.binary_operators)
        for two_behind, one_behind, current in iterator:
            if is_one_of_binary_operators(one_behind):
                new_children += [
                    Tree("binary_operation", [two_behind, one_behind, current])
                ]
                _, one_behind, current = advance(
                    iterator, times=2, default=(None, None, None)
                )
                if current is None:
                    break
            else:
                new_children += [two_behind]
        else:
            new_children += [item for item in [one_behind, current] if item is not None]
        return Tree("arguments", new_children)


class IsolateNotExpressions(IsolateUnaryOperators):
    unary_operators: List[str] = ["NOT"]


def IsolateConditions() -> Transformer:
    return TransformerChain(
        IsolateUnaryTests(), IsolateBinaryTests(), IsolateNotExpressions()
    )


class ConditionSyntaxCommandInvocationDumper(ArgumentAwareCommandInvocationDumper):
    one_value_keywords = ["AND", "OR"]

    def _format_group(self, group: Nodes) -> str:
        result = self._try_to_format_into_single_line(group, separator=" ")
        if result is not None:
            return result

        keyword, *values = group
        begin = self.visit(keyword)
        if len(values) == 0:
            return begin

        formatted_keys = "\n".join(self.visit(value) for value in values)
        if contains_line_comment([keyword]):
            return f"{begin}\n{self._indent(formatted_keys)}"
        return f"{begin} {formatted_keys.lstrip()}"

    def unary_operation(self, tree):
        result = self._try_to_format_into_single_line(tree.children, separator=" ")
        if result is not None:
            return result

        operation, arg = tree.children
        formatted_operation = self.visit(operation)
        with self.indented():
            formatted_arg = self.visit(arg)
        return f"{formatted_operation}\n{formatted_arg}"

    def binary_operation(self, tree):
        result = self._try_to_format_into_single_line(tree.children, separator=" ")
        if result is not None:
            return result

        lhs, operation, rhs = tree.children
        formatted_lhs = self.visit(lhs)
        with self.indented():
            formatted_operation = self.visit(operation)
            formatted_rhs = self.visit(rhs)
        return f"{formatted_lhs}\n{formatted_operation}\n{formatted_rhs}"

    def arguments(self, tree):
        preprocessed = IsolateConditions().transform(tree)
        return super().arguments(preprocessed)
