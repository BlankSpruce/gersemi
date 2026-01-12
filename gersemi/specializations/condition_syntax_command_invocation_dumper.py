from typing import List
from lark import Tree
from gersemi.ast_helpers import (
    is_comment,
    is_line_comment_in,
    is_one_of_keywords,
)
from gersemi.base_command_invocation_dumper import (
    BaseCommandInvocationDumper,
    ExpansionLimits,
    EXPANSION_LIMITS_INHIBIT_FAVOUR_EXPANSION,
)
from gersemi.configuration import Spaces
from gersemi.types import Nodes
from gersemi.utils import advance


def isolate_unary_operators(operators: List[str], children):
    one_behind = advance(children, times=1, default=None)
    if one_behind is None:
        return

    for current in children:
        if is_one_of_keywords(operators, one_behind):
            if is_comment(current):
                yield Tree("unary_operation", [one_behind])
                yield current
            else:
                yield Tree("unary_operation", [one_behind, current])
            current = advance(children, times=1, default=None)
            if current is None:
                break
        else:
            yield one_behind

        one_behind = current
    else:
        yield one_behind


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
    "IS_READABLE",
    "IS_WRITABLE",
    "IS_EXECUTABLE",
]
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
    "PATH_EQUAL",
]


def isolate_binary_tests(children):
    two_behind = advance(children, times=1, default=None)
    if two_behind is None:
        return

    one_behind = advance(children, times=1, default=None)
    if one_behind is None:
        yield two_behind
        return

    for current in children:
        if is_one_of_keywords(binary_operators, one_behind):
            yield Tree("binary_operation", [two_behind, one_behind, current])

            one_behind = advance(children, times=1, default=None)
            if one_behind is None:
                break

            current = advance(children, times=1, default=None)
            if current is None:
                yield one_behind
                break
        else:
            yield two_behind

        two_behind, one_behind = one_behind, current
    else:
        yield two_behind
        yield one_behind


def isolate_conditions(arguments: Nodes) -> Nodes:
    return isolate_unary_operators(
        ["OR"],
        isolate_unary_operators(
            ["AND"],
            isolate_unary_operators(
                ["NOT"],
                isolate_binary_tests(
                    isolate_unary_operators(unary_operators, iter(arguments))
                ),
            ),
        ),
    )


class ConditionSyntaxCommandInvocationDumper(BaseCommandInvocationDumper):
    expansion_limits: ExpansionLimits = EXPANSION_LIMITS_INHIBIT_FAVOUR_EXPANSION

    def unary_operation(self, tree):
        result = self._try_to_format_into_single_line(tree.children)
        if result is not None:
            return result

        operation, *rest = tree.children
        formatted_operation = self.visit(operation)
        if len(rest) == 0:
            return formatted_operation

        arg, *_ = rest
        if (
            (not is_line_comment_in(operation))
            and isinstance(self.indent_type, Spaces)
            and (len(formatted_operation.strip()) < self.indent_type)
        ):
            return f"{formatted_operation} {self.visit(arg).lstrip()}"

        with self.indented():
            formatted_arg = self.visit(arg)
        return f"{formatted_operation}\n{formatted_arg}"

    def binary_operation(self, tree):
        result = self._try_to_format_into_single_line(tree.children)
        if result is not None:
            return result

        lhs, operation, rhs = tree.children
        formatted_lhs = self.visit(lhs)
        with self.indented():
            formatted_operation = self.visit(operation)
            formatted_rhs = self.visit(rhs)
        return f"{formatted_lhs}\n{formatted_operation}\n{formatted_rhs}"

    def _preprocess_arguments(self, arguments):
        return Tree("arguments", list(isolate_conditions(arguments.children)))

    def _split_arguments(self, arguments):
        if len(arguments) < 1:
            return arguments

        head, *tail = arguments
        return [[head], tail]

    def complex_argument(self, tree):
        arguments, *_ = tree.children
        arguments = self._preprocess_arguments(arguments)
        result = self._try_to_format_into_single_line(
            arguments.children, prefix="(", postfix=")"
        )
        if result is not None:
            return result

        begin = self._indent("(\n")
        with self.indented():
            formatted_arguments = self.visit(arguments)
        end = self._indent(")")
        return f"{begin}{formatted_arguments}\n{end}"


condition_syntax_commands = {
    key: {"__impl": ConditionSyntaxCommandInvocationDumper}
    for key in (
        "elseif",
        "else",
        "endif",
        "endwhile",
        "if",
        "while",
    )
}
