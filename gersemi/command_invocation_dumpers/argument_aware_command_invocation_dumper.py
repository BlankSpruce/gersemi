from typing import Dict, Iterator, Iterable, List, Optional, Sized, Tuple
from gersemi.ast_helpers import is_one_of_keywords, is_comment
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.types import Nodes
from gersemi.utils import pop_all


def to_list_of_single_item_lists(sequence):
    return [*map(lambda item: [item], sequence)]


def is_non_empty(sequence: Sized) -> bool:
    return len(sequence) > 0


def is_empty(sequence: Sized) -> bool:
    return len(sequence) <= 0


class KeywordSplitter:
    def __init__(self, options, one_value_keywords, multi_value_keywords):
        self.is_one_of_options = is_one_of_keywords(options)
        self.is_one_of_one_value_keywords = is_one_of_keywords(one_value_keywords)
        self.is_one_of_multi_value_keywords = is_one_of_keywords(multi_value_keywords)
        self.groups: List[Nodes] = []
        self.accumulator: Nodes = []
        self.comment_accumulator: Nodes = []

    def _flush_accumulators(self):
        each_comment_in_its_own_group = [[c] for c in pop_all(self.comment_accumulator)]
        argument_group = pop_all(self.accumulator)
        self.groups += [argument_group, *each_comment_in_its_own_group]

    def _append_option_group(self, argument):
        self._flush_accumulators()
        self.groups += [[argument]]

    def _append_one_value_group(self, argument, iterator):
        self._flush_accumulators()
        next_argument = next(iterator, None)
        if next_argument is None:
            self.groups += [[argument]]
        else:
            self.groups += [[argument, next_argument]]

    def split(self, arguments: Nodes) -> Tuple[Iterator[Nodes], Nodes]:
        iterator = iter(arguments)
        tail: Optional[Nodes] = None
        for argument in iterator:
            if is_comment(argument):
                self.comment_accumulator += [argument]
            elif self.is_one_of_options(argument):
                self._append_option_group(argument)
            elif self.is_one_of_one_value_keywords(argument):
                self._append_one_value_group(argument, iterator)
            elif self.is_one_of_multi_value_keywords(argument):
                self._flush_accumulators()
                self.accumulator = [argument]
            elif is_non_empty(self.accumulator):
                self.accumulator += [*pop_all(self.comment_accumulator), argument]
            else:
                tail = [argument, *iterator]
                break

        self._flush_accumulators()
        if tail is None:
            tail = [*iterator]
        return filter(is_non_empty, self.groups), tail


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
        splitter = KeywordSplitter(
            self.options, self.one_value_keywords, self.multi_value_keywords
        )
        return splitter.split(arguments)

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
