from contextlib import contextmanager
import re
from typing import Iterable, Mapping
from gersemi.ast_helpers import is_commented_argument
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


Sections = Mapping[str, Mapping[str, Iterable[str]]]


class Match(str):
    def __eq__(self, other):
        return re.search(self, other) is not None

    def __hash__(self):
        return hash(str(self))


def create_section_patch(section, old_class):
    def get(key):
        return section.get(key, [])

    class Impl(old_class):
        options = get("options")
        one_value_keywords = get("one_value_keywords")
        multi_value_keywords = get("multi_value_keywords")

    return Impl


class SectionAwareCommandInvocationDumper(ArgumentAwareCommandInvocationDumper):
    sections: Sections = {}

    @contextmanager
    def _update_section_characteristics(self, keyword):
        old_class = type(self)
        try:
            self.__class__ = create_section_patch(self.sections[keyword], old_class)
            yield
        finally:
            self.__class__ = old_class

    def _get_matcher(self, keyword):
        for item in self.sections:
            if Match(item) == keyword:
                return item
        return None

    def _format_group(self, group) -> str:
        result = self._try_to_format_into_single_line(group, separator=" ")
        if result is not None:
            return result

        original_format_group = super()._format_group
        front_node, *rest = group
        if is_commented_argument(front_node):
            inner, *_ = front_node.children
            keyword, *_ = inner.children
        else:
            keyword, *_ = front_node.children

        keyword_matcher = self._get_matcher(keyword)
        if keyword_matcher is None:
            return original_format_group(group)

        with self._update_section_characteristics(keyword_matcher):
            subgroups = self._split_arguments(rest)
            formatted_front = original_format_group([front_node])
            with self.indented():
                return "\n".join(
                    [formatted_front, *map(original_format_group, subgroups)]
                )
