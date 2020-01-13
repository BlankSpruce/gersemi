from lark import Tree
from lark.visitors import Interpreter
from gersemi.ast_helpers import is_newline
from gersemi.base_dumper import BaseDumper


def has_line_comments(node) -> bool:
    class Impl(Interpreter):
        def __default__(self, _) -> bool:
            return False

        def line_comment(self, _) -> bool:
            return True

        def _visit(self, tree: Tree) -> bool:
            is_subtree = lambda node: isinstance(node, Tree)
            subtrees = filter(is_subtree, tree.children)
            return any(map(self.visit, subtrees))

        arguments = _visit
        commented_argument = _visit

    return isinstance(node, Tree) and Impl().visit(node)


class CommandInvocationDumper(BaseDumper):
    def command_invocation(self, tree):
        identifier, arguments = tree.children
        begin = self._indent(f"{identifier}(")
        result = self._format_listable_content(begin, arguments)

        if "\n" in result or has_line_comments(arguments):
            result += f"\n{self._indent(')')}"
        else:
            result += ")"
        return result

    def arguments(self, tree):
        non_newline_elements = [
            child for child in tree.children if not is_newline(child)
        ]
        if not has_line_comments(tree) and len(non_newline_elements) <= 4:
            helper_tree = Tree("arguments", non_newline_elements)
            result = self._try_to_format_into_single_line(helper_tree)
            if result is not None:
                return result

        return "\n".join(self.visit(child) for child in non_newline_elements)

    def commented_argument(self, tree):
        argument, *_, comment = tree.children
        begin = "".join(self.visit_children(argument)) + " "
        return self._format_listable_content(begin, comment)

    def complex_argument(self, tree):
        arguments, *_ = tree.children
        begin = self._indent("(")
        result = self._format_listable_content(begin, arguments)
        if "\n" in result or has_line_comments(arguments):
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
