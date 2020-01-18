from typing import Iterator, List, Sized
from gersemi.ast_helpers import contains_line_comment, is_keyword
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.types import Node, Nodes


def is_one_of_keywords(argument: Node, keywords: List[str]) -> bool:
    predicates = map(is_keyword, keywords)
    invoke = lambda predicate: predicate(argument)
    return any(map(invoke, predicates))


def is_non_empty(l: Sized) -> bool:
    return len(l) != 0


def split_by_keywords(arguments: Nodes, keywords: List[str]) -> Iterator[Nodes]:
    groups: List[Nodes] = []
    last_group: Nodes = []
    for argument in arguments:
        if is_one_of_keywords(argument, keywords):
            groups.append(last_group)
            last_group = []
        last_group.append(argument)
    groups.append(last_group)
    return filter(is_non_empty, groups)


class KeywordAwareCommandInvocationDumper(BaseCommandInvocationDumper):
    def _format_group(self, group: Nodes) -> str:
        result = self._try_to_format_into_single_line(group, separator=" ")
        if result is not None:
            return result

        keyword, *values = group
        begin = self.visit(keyword)
        if len(values) == 0:
            return begin

        formatted_keys = self._indent("\n".join(self.visit(value) for value in values))
        return f"{begin}\n{formatted_keys}"

    def format_command(self, tree):
        identifier, arguments = tree.children
        if not contains_line_comment(tree.children):
            result = self._try_to_format_into_single_line(
                [identifier, "(", " ".join(self.visit_children(arguments)), ")"]
            )
            if result is not None:
                return result

        begin = self._indent(f"{identifier}(")
        dumper = type(self)(self.alignment + self.indent_size)
        formatted_arguments = dumper.visit(arguments)
        end = self._indent(")")
        return f"{begin}\n{formatted_arguments}\n{end}"
