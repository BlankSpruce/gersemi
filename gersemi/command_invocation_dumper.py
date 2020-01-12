from lark import Tree
from lark.visitors import Interpreter
from gersemi.ast_helpers import is_whitespace
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
        identifier, left_parenthesis, arguments, right_parenthesis = tree.children
        begin = self._indent(self.visit(identifier) + left_parenthesis)
        result = self._format_listable_content(begin, arguments)

        if "\n" in result or has_line_comments(arguments):
            result += "\n" + self._indent(right_parenthesis)
        else:
            result += right_parenthesis
        return result

    def arguments(self, tree):
        non_whitespace_elements = [
            child for child in tree.children if not is_whitespace(child)
        ]
        if not has_line_comments(tree) and len(non_whitespace_elements) <= 4:
            helper_tree = Tree("arguments", non_whitespace_elements)
            result = self._try_to_format_into_single_line(helper_tree)
            if result is not None:
                return result

        return "\n".join(self.visit(child) for child in non_whitespace_elements)

    def commented_argument(self, tree):
        argument, *_, comment = tree.children
        begin = "".join(self.visit_children(argument)) + " "
        return self._format_listable_content(begin, comment)

    def bracket_comment(self, tree):
        return " " * self.alignment + self.__default__(tree)

    def bracket_argument(self, tree):
        return " " * self.alignment + self.__default__(tree)

    def quoted_argument(self, tree):
        return " " * self.alignment + self.__default__(tree)

    def unquoted_argument(self, tree):
        return self._indent(self.__default__(tree))
