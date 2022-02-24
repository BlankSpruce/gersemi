from contextlib import contextmanager
from typing import Dict, Iterable
from gersemi.ast_helpers import is_commented_argument
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class SectionAwareCommandInvocationDumper(ArgumentAwareCommandInvocationDumper):
    sections: Dict[str, Dict[str, Iterable[str]]] = {}

    @contextmanager
    def _update_section_characteristics(self, keyword):
        try:
            section = self.sections[keyword]
            self.options = section.get("options", [])
            self.one_value_keywords = section.get("one_value_keywords", [])
            self.multi_value_keywords = section.get("multi_value_keywords", [])
            yield
        finally:
            delattr(self, "options")
            delattr(self, "one_value_keywords")
            delattr(self, "multi_value_keywords")

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

        if keyword not in self.sections:
            return original_format_group(group)

        with self._update_section_characteristics(keyword):
            subgroups = self._split_arguments(rest)
            formatted_front = original_format_group([front_node])
            with self.indented():
                return "\n".join(
                    [formatted_front, *map(original_format_group, subgroups)]
                )
