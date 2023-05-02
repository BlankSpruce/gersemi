from typing import Dict, Iterator, Iterable, List, Sequence, Sized, Tuple
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


class PositionalArguments(list):
    pass


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
        if isinstance(self.accumulator, PositionalArguments):
            argument_group = PositionalArguments(pop_all(self.accumulator))
        else:
            argument_group = pop_all(self.accumulator)
        self.groups += [argument_group, *each_comment_in_its_own_group]

    def _append_option_group(self, argument):
        self._flush_accumulators()
        self.groups += [[argument]]

    def _append_one_value_group(self, argument, iterator):
        self._flush_accumulators()
        group = [argument]
        for n in iterator:
            group.append(n)
            if not is_comment(n):
                break
        self.groups.append(group)

    def split(self, arguments: Nodes) -> Iterator[Nodes]:
        iterator = iter(arguments)
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
                if not isinstance(self.accumulator, PositionalArguments):
                    self.accumulator = PositionalArguments()
                self.accumulator += [*pop_all(self.comment_accumulator), argument]

        self._flush_accumulators()
        return filter(is_non_empty, self.groups)


class ArgumentAwareCommandInvocationDumper(BaseCommandInvocationDumper):
    inhibit_favour_expansion: bool = False
    front_positional_arguments: Sequence[str] = []
    back_positional_arguments: Sequence[str] = []
    options: Iterable[str] = []
    one_value_keywords: Iterable[str] = []
    multi_value_keywords: Iterable[str] = []
    keyword_formatters: Dict[str, str] = {}

    def _default_format_values(self, values) -> str:
        return "\n".join(map(self.visit, values))

    def _format_positional_arguments_group(self, group) -> str:
        return "\n".join(map(self.visit, group))

    def _format_group(self, group) -> str:
        if isinstance(group, PositionalArguments):
            return self._format_positional_arguments_group(group)

        result = self._try_to_format_into_single_line(group, separator=" ")
        if result is not None:
            return result

        keyword, *values = group
        keyword_as_value = keyword.children[0] if len(keyword.children) > 0 else None

        can_be_inlined = (not self.favour_expansion) or (
            self.favour_expansion
            and keyword is not None
            and keyword_as_value not in self.multi_value_keywords
        )
        if can_be_inlined:
            with self.select_inlining_strategy():
                result = self._try_to_format_into_single_line(group, separator=" ")
                if result is not None:
                    return result

        begin = self.visit(keyword)
        if len(values) == 0:
            return begin

        with self.indented():
            formatter = getattr(
                self,
                self.keyword_formatters.get(keyword_as_value, "_default_format_values"),
            )
            formatted_values = formatter(values)
        return f"{begin}\n{formatted_values}"

    def _split_positional_arguments(self, arguments: Nodes, positional_arguments):
        last_index = min(len(arguments), len(positional_arguments))
        result = []
        for i in range(last_index):
            result.append(PositionalArguments([arguments[i]]))

        rest = arguments[last_index:]
        if len(rest) > 0:
            result.append(PositionalArguments(rest))
        return result

    def _separate_front(self, arguments: Nodes) -> Tuple[List[Nodes], Nodes]:
        is_keyword = is_one_of_keywords(
            list(self.options)
            + list(self.one_value_keywords)
            + list(self.multi_value_keywords)
        )
        for index, argument in enumerate(arguments):
            if is_keyword(argument):
                pivot = index
                break
        else:
            return (
                self._split_positional_arguments(
                    arguments, self.front_positional_arguments
                ),
                [],
            )
        return (
            self._split_positional_arguments(
                arguments[:pivot], self.front_positional_arguments
            ),
            arguments[pivot:],
        )

    def _split_by_keywords(self, arguments: Nodes) -> Iterator[Nodes]:
        splitter = KeywordSplitter(
            self.options,
            self.one_value_keywords,
            self.multi_value_keywords,
        )
        return splitter.split(arguments)

    def _split_arguments(self, arguments):
        if len(self.back_positional_arguments) > 0:
            arguments, back = (
                arguments[: -len(self.back_positional_arguments)],
                [
                    PositionalArguments(
                        arguments[-len(self.back_positional_arguments) :]
                    )
                ],
            )
        else:
            back = []
        front, tail = self._separate_front(arguments)
        keyworded_arguments = self._split_by_keywords(tail)

        return [*front, *keyworded_arguments, *back]

    def group_size(self, group):
        if isinstance(group, PositionalArguments):
            return len(group)
        return max(0, len(group) - 1)

    def arguments(self, tree):
        groups = self._split_arguments(tree.children)
        return "\n".join(map(self._format_group, filter(None, groups)))
