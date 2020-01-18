from .keyword_aware_command_invocation_dumper import (
    KeywordAwareCommandInvocationDumper,
    split_by_keywords,
)


class ExecuteProcessCommandDumper(KeywordAwareCommandInvocationDumper):
    def arguments(self, tree):
        keywords = [
            "COMMAND",
            "WORKING_DIRECTORY",
            "TIMEOUT",
            "RESULT_VARIABLE",
            "RESULTS_VARIABLE",
            "OUTPUT_VARIABLE",
            "ERROR_VARIABLE",
            "INPUT_FILE",
            "OUTPUT_FILE",
            "ERROR_FILE",
            "OUTPUT_QUIET",
            "ERROR_QUIET",
            "COMMAND_ECHO",
            "OUTPUT_STRIP_TRAILING_WHITESPACE",
            "ERROR_STRIP_TRAILING_WHITESPACE",
            "ENCODING",
        ]
        groups = split_by_keywords(tree.children, keywords)
        return "\n".join(map(self._format_group, groups))
