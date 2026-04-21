from typing import Dict, Iterable, Optional, Sequence
import gersemi_rust_backend
from gersemi.ast_helpers import (
    get_value,
    is_multi_value_argument,
    is_one_value_argument,
    is_option_argument,
    is_pair,
    is_positional_arguments,
    is_section,
)
from gersemi.base_command_invocation_dumper import BaseCommandInvocationDumper
from gersemi.keyword_kind import (
    KeywordFormatter,
    KeywordPreprocessor,
    kind_to_formatter,
    kind_to_preprocessor,
)
from gersemi.keywords import KeywordMatcher


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
            keyword is not None
            and (not is_pair(tree))
            and (not is_multi_value_argument(tree))
        )
        if can_be_inlined:
            with self.select_inlining_strategy():
                result = self._try_to_format_into_single_line(tree.children)
                if result is not None:
                    return result

        begin = self.visit(keyword)
        if len(values) == 0:
            return begin

        formatter_kind = self._get_formatter(keyword_as_value)
        if formatter_kind is None:
            formatter_kind = self._keyword_formatters.get(
                keyword_as_value, "_default_format_values"
            )

        with self.indented():
            formatter = getattr(self, formatter_kind)
            formatted_values = formatter(values)
        return f"{begin}\n{formatted_values}"

    def _split_arguments(self, arguments):
        return gersemi_rust_backend.argument_aware_split_arguments(
            self,
            arguments,
        )

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

    def pair(self, tree):
        return self._format_non_option(tree)

    def _get_formatter(self, tree):
        return kind_to_formatter(
            self.keyword_formatters.get(get_value(tree, None), None)
        )

    def _get_preprocessor(self, tree):
        return kind_to_preprocessor(
            self.keyword_preprocessors.get(get_value(tree, None), None)
        )

    def multi_value_argument(self, tree):
        keyword, *values = tree.children
        preprocessor = self._get_preprocessor(keyword)
        if preprocessor is not None:
            tree.children = [keyword, *getattr(self, preprocessor)(values)]

        return self._format_non_option(tree)

    def arguments(self, tree):
        groups = self._split_arguments(tree.children)
        return "\n".join(map(self.visit, filter(None, groups)))
