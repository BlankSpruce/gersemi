from itertools import dropwhile, takewhile
from lark import Tree
from lark.visitors import Interpreter
from gersemi.ast_helpers import is_unquoted_argument
from gersemi.base_dumper import BaseDumper


def contains_line_comment(nodes) -> bool:
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

    check_node = lambda node: isinstance(node, Tree) and Impl().visit(node)
    return any(map(check_node, nodes))


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
            result = self._try_to_format_into_single_line(tree.children)
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


def just_values(children):
    is_not_keyword = lambda child: not is_cache(child) and not is_parent_scope(child)
    return list(takewhile(is_not_keyword, children[1:]))


def is_unquoted(argument):
    def impl(node):
        return is_unquoted_argument(node) and node.children[0] == argument

    return impl


is_parent_scope = is_unquoted("PARENT_SCOPE")
is_cache = is_unquoted("CACHE")
is_force = is_unquoted("FORCE")


class SetCommandDumper(BaseCommandInvocationDumper):
    @staticmethod
    def _can_be_formatted_into_single_line(children):
        return not contains_line_comment(children) and len(just_values(children)) <= 4

    @staticmethod
    def _is_cache_type(children):
        return any(map(is_cache, children))

    def _format_cache_part(self, children):
        result = self._try_to_format_into_single_line(children)
        if result is not None:
            return result

        cache, cache_type, docstring = map(self.visit, children)
        return f"{cache} {cache_type.lstrip()}\n{docstring}"

    def _format_name_and_values(self, children):
        if self._can_be_formatted_into_single_line(children):
            result = self._try_to_format_into_single_line(children)
            if result is not None:
                return result

        return "\n".join(map(self.visit, children))

    def _cache_arguments(self, tree):
        if is_force(tree.children[-1]):
            *begin, force = tree.children
        else:
            begin, force = tree.children, None
        is_not_cache = lambda child: not is_cache(child)
        name_and_values = [*takewhile(is_not_cache, begin)]
        cache_part = [*dropwhile(is_not_cache, begin)]

        formatted_begin = self._format_name_and_values(name_and_values)
        formatted_cache_part = self._format_cache_part(cache_part)
        formatted_force = "" if force is None else "\n" + self.visit(force)
        return f"{formatted_begin}\n{formatted_cache_part}{formatted_force}"

    def arguments(self, tree):
        if self._can_be_formatted_into_single_line(tree.children):
            result = self._try_to_format_into_single_line(tree.children)
            if result is not None:
                return result

        if self._is_cache_type(tree.children):
            return self._cache_arguments(tree)

        return "\n".join(self.visit_children(tree))


class CommandInvocationDumper(BaseCommandInvocationDumper):
    known_command_mapping = {
        "set": SetCommandDumper,
    }

    def _patch_dumper(self, patch):
        original_dumper = type(self)

        class Impl(patch, original_dumper):
            pass

        return Impl(self.alignment)

    def _get_patch(self, command_name):
        return self.known_command_mapping.get(command_name, None)

    def command_invocation(self, tree):
        command_name, _ = tree.children
        patch = self._get_patch(command_name)
        if patch is None:
            return super().format_command(tree)
        return self._patch_dumper(patch).format_command(tree)
