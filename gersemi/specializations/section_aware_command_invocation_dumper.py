from contextlib import contextmanager
from typing import Iterable, Mapping
from lark import Tree
from gersemi.ast_helpers import (
    get_value,
    is_one_value_argument,
    is_multi_value_argument,
    is_one_of_keywords,
    is_positional_arguments,
    is_section,
    positional_arguments,
)
from gersemi.keyword_kind import kind_to_preprocessor
from gersemi.keywords import KeywordMatcher
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


Sections = Mapping[KeywordMatcher, Mapping[KeywordMatcher, Iterable[KeywordMatcher]]]


def create_section_patch(section, old_class):
    def get(key, default_value):
        return section.get(key, default_value)

    class Impl(old_class):
        front_positional_arguments = get("front_positional_arguments", [])
        back_positional_arguments = get("back_positional_arguments", [])
        options = get("options", [])
        one_value_keywords = get("one_value_keywords", [])
        multi_value_keywords = get("multi_value_keywords", [])
        sections = get("sections", dict())
        keyword_formatters = get("keyword_formatters", dict())
        keyword_preprocessors = get("keyword_preprocessors", dict())

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

    def _is_among_section_keywords(self, section_matcher, argument):
        if section_matcher is None:
            return False

        with self._update_section_characteristics(section_matcher):
            for keywords in (
                self.options,
                self.one_value_keywords,
                self.multi_value_keywords,
            ):
                if is_one_of_keywords(keywords)(argument.children[0]):
                    return True

        return False

    def _fix_back_positional_arguments(self, section):
        if not is_section(section):
            return section

        pivot = len(self.back_positional_arguments)
        if pivot == 0:
            return section

        *front, last = section.children
        if is_one_value_argument(last) or is_multi_value_argument(last):
            last_front, *last_rest = last.children
            left_in_place, back_positional_arguments = (
                last_rest[:-pivot],
                last_rest[-pivot:],
            )
            last.children = [last_front, *left_in_place]
            section.children = [
                *front,
                last,
                positional_arguments(back_positional_arguments),
            ]

        return section

    def _form_sections(self, arguments):
        result = []
        section_matcher = None
        for argument in arguments:
            if self._is_among_section_keywords(section_matcher, argument):
                result[-1].children.append(argument)
            else:
                if section_matcher is not None:
                    with self._update_section_characteristics(section_matcher):
                        result[-1] = self._fix_back_positional_arguments(result[-1])

                if len(argument.children) > 0:
                    section_matcher = self._get_matcher(argument.children[0])
                else:
                    section_matcher = None

                result.append(argument)

        return self._fix_back_positional_arguments(result)

    def _split_arguments(self, arguments):
        preprocessed = super()._split_arguments(arguments)
        return self._form_sections(
            (
                self._split_multi_value_argument(child)
                if is_multi_value_argument(child)
                else child
            )
            for child in preprocessed
        )

    def section(self, tree):
        header, *rest = tree.children
        preprocessor = kind_to_preprocessor(
            self.keyword_preprocessors.get(get_value(header, None), None)
        )
        if preprocessor is not None:

            rest = getattr(self, preprocessor)(rest)

        result = self._try_to_format_into_single_line(tree.children)
        if result is not None:
            return result

        begin = self.visit(header)
        if len(rest) == 0:
            return begin

        with self.indented():
            formatted_values = "\n".join(map(self.visit, rest))
        return f"{begin}\n{formatted_values}"
