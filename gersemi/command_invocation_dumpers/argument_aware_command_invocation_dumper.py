from typing import Dict, Iterator, Iterable, List, Optional, Sized, Tuple
from gersemi.ast_helpers import is_one_of_keywords
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.types import Nodes
from gersemi.utils import pop_all


def to_list_of_single_item_lists(sequence):
    return [*map(lambda item: [item], sequence)]


def is_non_empty(sequence: Sized) -> bool:
    return len(sequence) > 0


class ArgumentAwareCommandInvocationDumper(BaseCommandInvocationDumper):
    options: Iterable[str] = []
    one_value_keywords: Iterable[str] = []
    multi_value_keywords: Iterable[str] = []
    keyword_formatters: Dict[str, str] = {}

    def _default_format_values(self, values) -> str:
        return "\n".join(map(self.visit, values))

    def _format_group(self, group) -> str:
        result = self._try_to_format_into_single_line(group, separator=" ")
        if result is not None:
            return result

        keyword, *values = group
        begin = self.visit(keyword)
        if len(values) == 0:
            return begin

        keyword_as_value = keyword.children[0]
        with self.indented():
            formatter = getattr(
                self,
                self.keyword_formatters.get(keyword_as_value, "_default_format_values"),
            )
            formatted_values = formatter(values)
        return f"{begin}\n{formatted_values}"

    def _separate_front(self, arguments: Nodes) -> Tuple[List[Nodes], Nodes]:
        is_one_of_keywords_with_values = is_one_of_keywords(
            list(self.one_value_keywords) + list(self.multi_value_keywords)
        )
        for index, argument in enumerate(arguments):
            if is_one_of_keywords_with_values(argument):
                pivot = index
                break
        else:
            return to_list_of_single_item_lists(arguments), []
        return to_list_of_single_item_lists(arguments[:pivot]), arguments[pivot:]

    def _split_by_keywords(self, arguments: Nodes) -> Tuple[Iterator[Nodes], Nodes]:
        is_one_of_options = is_one_of_keywords(self.options)
        is_one_of_one_value_keywords = is_one_of_keywords(self.one_value_keywords)
        is_one_of_multi_value_keywords = is_one_of_keywords(self.multi_value_keywords)
        groups: List[Nodes] = []
        accumulator: Nodes = []
        tail: Optional[Nodes] = None
        iterator = iter(arguments)
        for argument in iterator:
            if is_one_of_options(argument):
                groups += [pop_all(accumulator)]
                groups += [[argument]]
            elif is_one_of_one_value_keywords(argument):
                groups += [pop_all(accumulator)]
                next_argument = next(iterator, None)
                if next_argument is None:
                    groups += [[argument]]
                else:
                    groups += [[argument, next_argument]]
            elif is_one_of_multi_value_keywords(argument):
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
        result = self._try_to_format_into_single_line(
            arguments.children, separator=" ", prefix=f"{identifier}(", postfix=")"
        )
        if result is not None:
            return result

        begin = self._indent(f"{identifier}(")
        with self.indented():
            formatted_arguments = self.visit(arguments)
        end = self._indent(")")
        return f"{begin}\n{formatted_arguments}\n{end}"

    def arguments(self, tree):
        groups = self._split_arguments(tree.children)
        return "\n".join(map(self._format_group, groups))
