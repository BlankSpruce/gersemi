from .keyword_aware_command_invocation_dumper import (
    KeywordAwareCommandInvocationDumper,
    split_by_keywords,
)


class CMakeHostSysteInformationCommandDumper(KeywordAwareCommandInvocationDumper):
    def arguments(self, tree):
        groups = split_by_keywords(tree.children, ["RESULT", "QUERY"])
        return "\n".join(map(self._format_group, groups))
