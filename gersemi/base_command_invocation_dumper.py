from typing import List
from gersemi.ast_helpers import contains_line_comment
from gersemi.base_dumper import BaseDumper
from gersemi.configuration import ListExpansion
from gersemi.types import Nodes


class BaseCommandInvocationDumper(BaseDumper):
    def format_command_with_short_name(self, begin, arguments, end):
        with self.indented():
            formatted_arguments = self.visit(arguments).lstrip()
        if (
            not contains_line_comment(arguments.children)
            and "\n" not in formatted_arguments
        ):
            return "".join([self._indent(begin), formatted_arguments, end])

        return f"{self._indent(begin)}{formatted_arguments}\n{self._indent(end)}"

    def _format_command_with_long_name(self, begin, arguments, end):
        with self.indented():
            formatted_arguments = self.visit(arguments)
        return "\n".join([self._indent(begin), formatted_arguments, self._indent(end)])

    def _split_arguments(self, arguments: Nodes) -> List[Nodes]:
        return [arguments]

    def group_size(self, group):
        return len(group)

    def _inlining_condition(self, arguments):
        groups = self._split_arguments(arguments.children)
        group_sizes = list(map(self.group_size, groups))
        if (
            self.list_expansion == ListExpansion.FavourExpansion
            and not self.inhibit_favour_expansion
        ):
            return all(size < 2 for size in group_sizes)
        return all(size <= 4 for size in group_sizes)

    def format_command(self, tree):
        identifier, arguments = tree.children
        arguments = self._preprocess_arguments(arguments)
        begin = f"{identifier}("
        end = ")"
        if self._inlining_condition(arguments):
            result = self._try_to_format_into_single_line(
                arguments.children, separator=" ", prefix=f"{identifier}(", postfix=")"
            )
            if result is not None:
                return result

        with self.select_expansion_strategy():
            if len(begin) == self.indent_size:
                return self.format_command_with_short_name(begin, arguments, end)
            return self._format_command_with_long_name(begin, arguments, end)

    def arguments(self, tree):
        return "\n".join(self.visit_children(tree))

    def commented_argument(self, tree):
        argument, comment, *_ = tree.children
        formatted_argument = self.visit(argument)
        with self.not_indented():
            formatted_comment = self.visit(comment)
        return f"{formatted_argument} {formatted_comment}"

    def complex_argument(self, tree):
        arguments, *_ = tree.children
        if len(arguments.children) <= 4:
            result = self._try_to_format_into_single_line(
                arguments.children, separator=" ", prefix="(", postfix=")"
            )
            if result is not None:
                return result

        begin = self._indent("(\n")
        with self.indented():
            formatted_arguments = self.visit(arguments)
        end = self._indent(")")
        return f"{begin}{formatted_arguments}\n{end}"

    def bracket_comment(self, tree):
        return " " * self.alignment + "#" + self.__default__(tree)

    def bracket_argument(self, tree):
        return " " * self.alignment + self.__default__(tree)

    def quoted_argument(self, tree):
        return " " * self.alignment + f'"{self.__default__(tree)}"'

    def unquoted_argument(self, tree):
        return self._indent(self.__default__(tree))

    def _preprocess_arguments(self, arguments):
        return arguments
