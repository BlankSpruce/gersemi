import gersemi_rust_backend
from gersemi.ast_helpers import is_line_comment_in
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.configuration import Spaces


class ConditionSyntaxCommandInvocationDumper(BaseCommandInvocationDumper):
    _inhibit_favour_expansion = True

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
        return gersemi_rust_backend.condition_syntax_preprocess_arguments(arguments)

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


class ConditionSyntaxCommandInvocationDumperWithDedent(
    ConditionSyntaxCommandInvocationDumper
):
    def format_command(self, tree):
        with self.dedented():
            return super().format_command(tree)


condition_syntax_commands = {
    key: {
        "__impl": ConditionSyntaxCommandInvocationDumperWithDedent
        if key in ("else", "elseif")
        else ConditionSyntaxCommandInvocationDumper
    }
    for key in (
        "elseif",
        "else",
        "endif",
        "endwhile",
        "if",
        "while",
    )
}
