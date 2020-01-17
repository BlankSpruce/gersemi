from gersemi.ast_helpers import contains_line_comment
from gersemi.base_dumper import BaseDumper


class BaseCommandInvocationDumper(BaseDumper):
    def format_command(self, tree):
        identifier, arguments = tree.children
        begin = self._indent(f"{identifier}(")
        result = self._format_listable_content(begin, arguments)

        if "\n" in result or contains_line_comment(arguments.children):
            result += f"\n{self._indent(')')}"
        else:
            result += ")"
        return result

    def arguments(self, tree):
        if not contains_line_comment(tree.children) and len(tree.children) <= 4:
            result = self._try_to_format_into_single_line(tree.children, separator=" ")
            if result is not None:
                return result

        return "\n".join(self.visit_children(tree))

    def commented_argument(self, tree):
        argument, *_, comment = tree.children
        begin = "".join(self.visit(argument)) + " "
        return self._format_listable_content(begin, comment)

    def complex_argument(self, tree):
        arguments, *_ = tree.children
        begin = self._indent("(")
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
