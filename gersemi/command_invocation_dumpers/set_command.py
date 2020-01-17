from itertools import dropwhile, takewhile
from gersemi.ast_helpers import contains_line_comment, is_keyword
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper


def can_be_formatted_into_single_line(children):
    return not contains_line_comment(children) and len(just_values(children)) <= 4


def just_values(children):
    is_not_keyword = lambda child: not is_cache(child) and not is_parent_scope(child)
    return list(takewhile(is_not_keyword, children[1:]))


is_parent_scope = is_keyword("PARENT_SCOPE")
is_cache = is_keyword("CACHE")
is_force = is_keyword("FORCE")


def is_cache_type(children):
    return any(map(is_cache, children))


class SetCommandDumper(BaseCommandInvocationDumper):
    def _format_cache_part(self, children):
        result = self._try_to_format_into_single_line(children, separator=" ")
        if result is not None:
            return result

        cache, cache_type, docstring = map(self.visit, children)
        return f"{cache} {cache_type.lstrip()}\n{docstring}"

    def _format_name_and_values(self, children):
        if can_be_formatted_into_single_line(children):
            result = self._try_to_format_into_single_line(children, separator=" ")
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
        if can_be_formatted_into_single_line(tree.children):
            result = self._try_to_format_into_single_line(tree.children, separator=" ")
            if result is not None:
                return result

        if is_cache_type(tree.children):
            return self._cache_arguments(tree)

        return "\n".join(self.visit_children(tree))
