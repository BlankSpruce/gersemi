from typing import Iterator, List, Optional, Sized, Tuple
from gersemi.ast_helpers import contains_line_comment, is_keyword
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.types import Node, Nodes
from gersemi.utils import pop_all


def is_one_of_keywords(argument: Node, keywords: List[str]) -> bool:
    predicates = map(is_keyword, keywords)
    invoke = lambda predicate: predicate(argument)
    return any(map(invoke, predicates))


def to_list_of_single_item_lists(l):
    return [*map(lambda item: [item], l)]


def is_non_empty(l: Sized) -> bool:
    return len(l) != 0


class ArgumentAwareCommandInvocationDumper(BaseCommandInvocationDumper):
    options: List[str] = []
    one_value_keywords: List[str] = []
    multi_value_keywords: List[str] = []

    def _format_group(self, group: Nodes) -> str:
        if not contains_line_comment(group):
            result = self._try_to_format_into_single_line(group, separator=" ")
            if result is not None:
                return result

        keyword, *values = group
        begin = self.visit(keyword)
        if len(values) == 0:
            return begin

        formatted_keys = "\n".join(self.indented.visit(value) for value in values)
        return f"{begin}\n{formatted_keys}"

    @property
    def _keywords(self):
        return self.one_value_keywords + self.multi_value_keywords

    def _separate_front(self, arguments: Nodes) -> Tuple[List[Nodes], Nodes]:
        for index, argument in enumerate(arguments):
            if is_one_of_keywords(argument, self._keywords):
                pivot = index
                break
        else:
            return to_list_of_single_item_lists(arguments), []
        return to_list_of_single_item_lists(arguments[:pivot]), arguments[pivot:]

    def _split_by_keywords(self, arguments: Nodes) -> Tuple[Iterator[Nodes], Nodes]:
        groups: List[Nodes] = []
        accumulator: Nodes = []
        tail: Optional[Nodes] = None
        iterator = iter(arguments)
        for argument in iterator:
            if is_one_of_keywords(argument, self.options):
                groups += [pop_all(accumulator)]
                groups += [[argument]]
            elif is_one_of_keywords(argument, self.one_value_keywords):
                groups += [pop_all(accumulator)]
                groups += [[argument, next(iterator)]]
            elif is_one_of_keywords(argument, self.multi_value_keywords):
                groups += [pop_all(accumulator)]
                accumulator = [argument]
            elif is_non_empty(accumulator):
                accumulator += [argument]
            else:
                tail = [argument, *iterator]
                break

        groups += [pop_all(accumulator)]
        if tail is None:
            tail = [*iterator]
        return filter(is_non_empty, groups), tail

    def _split_arguments(self, arguments: Nodes) -> List[Nodes]:
        front, tail = self._separate_front(arguments)
        keyworded_arguments, tail = self._split_by_keywords(tail)
        back = to_list_of_single_item_lists(tail)
        return [*front, *keyworded_arguments, *back]

    def format_command(self, tree):
        identifier, arguments = tree.children
        if not contains_line_comment(tree.children):
            result = self._try_to_format_into_single_line(
                arguments.children, separator=" ", prefix=f"{identifier}(", postfix=")"
            )
            if result is not None:
                return result

        begin = self._indent(f"{identifier}(")
        formatted_arguments = self.indented.visit(arguments)
        end = self._indent(")")
        return f"{begin}\n{formatted_arguments}\n{end}"

    def arguments(self, tree):
        groups = self._split_arguments(tree.children)
        return "\n".join(map(self._format_group, groups))
