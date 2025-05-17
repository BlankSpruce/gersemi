from collections.abc import Sized
from typing import Dict, Iterator, Iterable, List, Optional, Sequence, Tuple
from lark import Tree
from gersemi.ast_helpers import (
    get_value,
    is_comment,
    is_multi_value_argument,
    is_one_of_keywords,
    is_one_value_argument,
    is_option_argument,
    is_positional_arguments,
    is_section,
    option_argument,
    one_value_argument,
    multi_value_argument,
    positional_arguments,
)
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.keywords import KeywordMatcher
from gersemi.keyword_kind import (
    KeywordFormatter,
    KeywordPreprocessor,
    kind_to_formatter,
    kind_to_preprocessor,
)
from gersemi.types import Nodes
from gersemi.utils import pop_all


def is_non_empty(sequence: Sized) -> bool:
    return len(sequence) > 0


def is_non_empty_group(group: Sized) -> bool:
    if isinstance(group, Tree):
        return is_non_empty(group.children)

    return is_non_empty(group)


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
        if isinstance(self.accumulator, PositionalArguments):
            argument_group = positional_arguments(pop_all(self.accumulator))
        else:
            argument_group = multi_value_argument(pop_all(self.accumulator))
        self.groups += [argument_group, *pop_all(self.comment_accumulator)]

    def _append_option_group(self, argument):
        self._flush_accumulators()
        self.groups.append(option_argument([argument]))

    def _append_one_value_group(self, argument, iterator):
        self._flush_accumulators()
        group = [argument]
        for n in iterator:
            group.append(n)
            if not is_comment(n):
                break
        self.groups.append(one_value_argument(group))

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
        return filter(is_non_empty_group, self.groups)


class ArgumentAwareCommandInvocationDumper(BaseCommandInvocationDumper):
    _inhibit_favour_expansion: bool = False
    _keyword_formatters: Dict[str, str] = {}
    _canonical_name: Optional[str] = None

    front_positional_arguments: Sequence[str] = []
    back_positional_arguments: Sequence[str] = []
    options: Iterable[KeywordMatcher] = []
    one_value_keywords: Iterable[KeywordMatcher] = []
    multi_value_keywords: Iterable[KeywordMatcher] = []
    keyword_formatters: Dict[str, KeywordFormatter] = {}
    keyword_preprocessors: Dict[str, KeywordPreprocessor] = {}

    def _default_format_values(self, values) -> str:
        return "\n".join(map(self.visit, values))

    def positional_arguments(self, tree) -> str:
        return "\n".join(map(self.visit, tree.children))

    def _format_non_option(self, tree):
        result = self._try_to_format_into_single_line(tree.children)
        if result is not None:
            return result

        keyword, *values = tree.children
        keyword_as_value = get_value(keyword, None)

        can_be_inlined = (not self.favour_expansion) or (
            self.favour_expansion
            and keyword is not None
            and keyword_as_value not in self.multi_value_keywords
        )
        if can_be_inlined:
            with self.select_inlining_strategy():
                result = self._try_to_format_into_single_line(tree.children)
                if result is not None:
                    return result

        begin = self.visit(keyword)
        if len(values) == 0:
            return begin

        formatter_kind = kind_to_formatter(
            self.keyword_formatters.get(keyword_as_value, None)
        )
        if formatter_kind is None:
            formatter_kind = self._keyword_formatters.get(
                keyword_as_value, "_default_format_values"
            )

        with self.indented():
            formatter = getattr(self, formatter_kind)
            formatted_values = formatter(values)
        return f"{begin}\n{formatted_values}"

    def _split_positional_arguments(self, arguments: Nodes, known_positional_arguments):
        last_index = min(len(arguments), len(known_positional_arguments))
        result = []
        for i in range(last_index):
            result.append(positional_arguments([arguments[i]]))

        rest = arguments[last_index:]
        if len(rest) > 0:
            result.append(positional_arguments(rest))
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
                    positional_arguments(
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
        if is_positional_arguments(group):
            return len(group.children)
        if is_option_argument(group):
            return 0
        if is_one_value_argument(group):
            return len(group.children) - 1
        if is_multi_value_argument(group):
            return len(group.children) - 1
        if is_section(group):
            section_size = len(group.children) - 1
            subarguments_size = max(map(self.group_size, group.children))
            return max(section_size, subarguments_size)

        return 0

    def option_argument(self, tree):
        return self.visit(tree.children[0])

    def one_value_argument(self, tree):
        return self._format_non_option(tree)

    def multi_value_argument(self, tree):
        keyword, *values = tree.children
        preprocessor = kind_to_preprocessor(
            self.keyword_preprocessors.get(get_value(keyword, None), None)
        )
        if preprocessor is not None:
            tree.children = [keyword, *getattr(self, preprocessor)(values)]

        return self._format_non_option(tree)

    def arguments(self, tree):
        groups = self._split_arguments(tree.children)
        return "\n".join(map(self.visit, filter(None, groups)))

    def format_command_name(self, identifier):
        if self._canonical_name is None:
            return super().format_command_name(identifier)

        if self._canonical_name.lower() != identifier.lower():
            raise RuntimeError

        return self._canonical_name
