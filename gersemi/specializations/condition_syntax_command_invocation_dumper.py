import gersemi_rust_backend
from gersemi.ast_helpers import is_line_comment_in
from gersemi.configuration import Spaces
from gersemi.dumper import Dumper
from gersemi.types import Tree


class ConditionSyntaxCommandInvocationDumper(Dumper):
    _inhibit_favour_expansion = True

    def unary_operation(self, tree):
        result = self._try_to_format_into_single_line(
            tree.children, visitor=self.arguments_atom
        )
        if result is not None:
            return result

        operation, *rest = tree.children
        formatted_operation = self.arguments_atom(operation)
        if len(rest) == 0:
            return formatted_operation

        arg, *_ = rest
        if (
            (not is_line_comment_in(operation))
            and isinstance(self.indent_type, Spaces)
            and (len(formatted_operation.strip()) < self.indent_type)
        ):
            return f"{formatted_operation} {self.arguments_atom(arg).lstrip()}"

        with self.indented():
            formatted_arg = self.arguments_atom(arg)
        return f"{formatted_operation}\n{formatted_arg}"

    def binary_operation(self, tree):
        result = self._try_to_format_into_single_line(
            tree.children, visitor=self.arguments_atom
        )
        if result is not None:
            return result

        lhs, operation, rhs = tree.children
        formatted_lhs = self.arguments_atom(lhs)
        with self.indented():
            formatted_operation = self.arguments_atom(operation)
            formatted_rhs = self.arguments_atom(rhs)
        return f"{formatted_lhs}\n{formatted_operation}\n{formatted_rhs}"

    def _preprocess_arguments(self, arguments):
        return gersemi_rust_backend.condition_syntax_preprocess_arguments(arguments)

    def _split_arguments(self, arguments):
        if len(arguments) < 1:
            return arguments

        head, *tail = arguments
        return [[head], tail]

    def argument(self, child):
        kind = child.data if isinstance(child, Tree) else child.type
        if kind == "binary_operation":
            return self.binary_operation(child)
        if kind == "unary_operation":
            return self.unary_operation(child)
        return super().argument(child)

    def arguments(self, tree):
        return "\n".join(map(self.arguments_atom, tree.children))

    def complex_argument(self, tree):
        arguments, *_ = tree.children
        arguments = self._preprocess_arguments(arguments)
        result = self._try_to_format_into_single_line(
            arguments.children, prefix="(", postfix=")", visitor=self.arguments_atom
        )
        if result is not None:
            return result

        begin = self._indent("(\n")
        with self.indented():
            formatted_arguments = self.arguments(arguments)
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
