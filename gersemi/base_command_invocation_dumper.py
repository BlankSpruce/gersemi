from gersemi.ast_helpers import contains_line_comment
from gersemi.base_dumper import BaseDumper


class BaseCommandInvocationDumper(BaseDumper):
    def format_command_with_short_name(self, begin, arguments, end):
        formatted_arguments = self.indented.visit(arguments).lstrip()
        if (
            not contains_line_comment(arguments.children)
            and "\n" not in formatted_arguments
        ):
            return "".join([self._indent(begin), formatted_arguments, end])

        return "{}{}\n{}".format(
            self._indent(begin), formatted_arguments, self._indent(end)
        )

    def _format_command_with_long_name(self, begin, arguments, end):
        formatted_arguments = self.indented.visit(arguments)
        return "\n".join([self._indent(begin), formatted_arguments, self._indent(end)])

    def format_command(self, tree):
        identifier, arguments = tree.children
        begin = f"{identifier}("
        end = ")"
        if (
            not contains_line_comment(arguments.children)
            and len(arguments.children) <= 4
        ):
            result = self._try_to_format_into_single_line(
                arguments.children, separator=" ", prefix=begin, postfix=end
            )
            if result is not None:
                return result

        if len(begin) <= self.indent_size:
            return self.format_command_with_short_name(begin, arguments, end)
        return self._format_command_with_long_name(begin, arguments, end)

    def arguments(self, tree):
        return "\n".join(self.visit_children(tree))

    def commented_argument(self, tree):
        argument, *_, comment = tree.children
        begin = "".join(self.visit(argument)) + " "
        return self._format_listable_content(begin, comment)

    def complex_argument(self, tree):
        arguments, *_ = tree.children
        begin = self._indent("(")
        if (
            not contains_line_comment(arguments.children)
            and len(arguments.children) <= 4
        ):
            result = self._try_to_format_into_single_line(
                arguments.children, separator=" ", prefix="(", postfix=")"
            )
            if result is not None:
                return result

        result = self._format_listable_content(begin, arguments)
        if "\n" in result or contains_line_comment(arguments.children):
            result += f"\n{self._indent(')')}"
        else:
            result += ")"
        return result

    def bracket_comment(self, tree):
        return " " * self.alignment + self.__default__(tree)

    def bracket_argument(self, tree):
        return " " * self.alignment + self.__default__(tree)

    def quoted_argument(self, tree):
        return " " * self.alignment + f'"{self.__default__(tree)}"'

    def unquoted_argument(self, tree):
        return self._indent(self.__default__(tree))
