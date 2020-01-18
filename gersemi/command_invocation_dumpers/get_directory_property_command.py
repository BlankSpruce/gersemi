from gersemi.ast_helpers import is_keyword
from .keyword_aware_command_invocation_dumper import (
    KeywordAwareCommandInvocationDumper,
    split_by_keywords,
)


def is_definition_type(children):
    return any(map(is_keyword("DEFINITION"), children))


class GetDirectoryPropertyCommandDumper(KeywordAwareCommandInvocationDumper):
    def arguments(self, tree):
        if is_definition_type(tree.children):
            groups = split_by_keywords(tree.children, ["DIRECTORY", "DEFINITION"])
        else:
            *rest, property_name = tree.children
            groups = [*split_by_keywords(rest, ["DIRECTORY"]), [property_name]]
        return "\n".join(map(self._format_group, groups))
