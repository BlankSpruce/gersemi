from lark import Tree
from lark.visitors import Interpreter
from gersemi.ast_helpers import is_unquoted_argument
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


class BaseCommandInvocationDumper(BaseDumper):
    def format_command(self, tree):
        identifier, arguments = tree.children
        begin = self._indent(f"{identifier}(")
        result = self._format_listable_content(begin, arguments)

        if "\n" in result or has_line_comments(arguments):
            result += f"\n{self._indent(')')}"
        else:
            result += ")"
        return result

    def arguments(self, tree):
        if not has_line_comments(tree) and len(tree.children) <= 4:
            result = self._try_to_format_into_single_line(tree)
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


def is_parent_scope_flag(node):
    return is_unquoted_argument(node) and node.children[0] == "PARENT_SCOPE"


class SetCommandDumper(BaseCommandInvocationDumper):
    @staticmethod
    def _just_values(children):
        if children and is_parent_scope_flag(children[-1]):
            return children[1:-1]
        return children[1:]

    def arguments(self, tree):
        if not has_line_comments(tree) and len(self._just_values(tree.children)) <= 4:
            result = self._try_to_format_into_single_line(tree)
            if result is not None:
                return result

        return "\n".join(self.visit_children(tree))


class CommandInvocationDumper(BaseCommandInvocationDumper):
    known_command_mapping = {
        "set": SetCommandDumper,
    }

    def _patch_dumper(self, patch):
        dumper = type(self)
        return type(f"{dumper.__name__} with {patch.__name__}", (patch, dumper), {})(
            self.alignment
        )

    def _get_patch(self, command_name):
        return self.known_command_mapping.get(command_name, None)

    def command_invocation(self, tree):
        command_name, _ = tree.children
        patch = self._get_patch(command_name)
        if patch is None:
            return super().format_command(tree)
        return self._patch_dumper(patch).format_command(tree)
