from contextlib import contextmanager
from typing import Iterable, Mapping
from lark import Tree
from gersemi.ast_helpers import (
    is_multi_value_argument,
    is_one_of_keywords,
    is_positional_arguments,
)
from gersemi.keywords import KeywordMatcher
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


Sections = Mapping[KeywordMatcher, Mapping[KeywordMatcher, Iterable[KeywordMatcher]]]


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
            matcher = is_one_of_keywords([item])
            if matcher(keyword):
                return item
        return None

    def _split_multi_value_argument(self, tree):
        front_node, *rest = tree.children

        keyword_matcher = self._get_matcher(front_node)
        if keyword_matcher is None:
            return tree

        with self._update_section_characteristics(keyword_matcher):
            subarguments = [front_node]
            for arg in self._split_arguments(rest):
                if not is_positional_arguments(arg):
                    subarguments.append(arg)
                    continue

                subarguments.extend(arg.children)

            return Tree("section", subarguments)

    def _split_arguments(self, arguments):
        preprocessed = super()._split_arguments(arguments)
        return [
            (
                self._split_multi_value_argument(child)
                if is_multi_value_argument(child)
                else child
            )
            for child in preprocessed
        ]

    def section(self, tree):
        result = self._try_to_format_into_single_line(tree.children, separator=" ")
        if result is not None:
            return result

        header, *rest = tree.children
        begin = self.visit(header)
        if len(rest) == 0:
            return begin

        with self.indented():
            formatted_values = "\n".join(map(self.visit, rest))
        return f"{begin}\n{formatted_values}"
