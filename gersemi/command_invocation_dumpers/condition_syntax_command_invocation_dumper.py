from typing import List
from lark import Tree
from lark.visitors import Transformer, TransformerChain, Transformer_InPlace
from gersemi.types import Node, Nodes
from gersemi.utils import advance
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
    is_one_of_keywords,
)


class IsolateUnaryOperators(Transformer_InPlace):
    unary_operators: List[str] = []

    def arguments(self, children: Nodes) -> Tree:
        if len(children) < 2:
            return Tree("arguments", children)

        new_children: Nodes = []
        iterator = zip(children, children[1:])
        for one_behind, current in iterator:
            if is_one_of_keywords(one_behind, self.unary_operators):
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
        for two_behind, one_behind, current in iterator:
            if is_one_of_keywords(one_behind, self.binary_operators):
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
        IsolateUnaryTests(), IsolateBinaryTests(), IsolateNotExpressions(),
    )


def is_boolean_operator(argument: Node) -> bool:
    return is_one_of_keywords(argument, ["AND", "OR"])


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
        return f"{begin} {formatted_keys.lstrip()}"

    def complex_argument(self, tree):
        arguments, *_ = tree.children
        result = self._try_to_format_into_single_line(
            arguments.children, separator=" ", prefix="(", postfix=")"
        )
        if result is not None:
            return result

        begin = "(\n"
        formatted_arguments = self.indented.visit(arguments)
        end = self._indent(")")
        return f"{begin}{formatted_arguments}\n{end}"

    def unary_operation(self, tree):
        result = self._try_to_format_into_single_line(tree.children, separator=" ")
        if result is not None:
            return result

        operation, arg = tree.children
        formatted_operation = self.visit(operation)
        formatted_arg = self.indented.visit(arg)
        return f"{formatted_operation}\n{formatted_arg}"

    def binary_operation(self, tree):
        result = self._try_to_format_into_single_line(tree.children, separator=" ")
        if result is not None:
            return result

        lhs, operation, rhs = tree.children
        formatted_lhs = self.visit(lhs)
        dumper = self.indented
        formatted_operation = dumper.visit(operation)
        formatted_rhs = dumper.visit(rhs)
        return f"{formatted_lhs}\n{formatted_operation}\n{formatted_rhs}"

    def arguments(self, tree):
        preprocessed = IsolateConditions().transform(tree)
        return super().arguments(preprocessed)
