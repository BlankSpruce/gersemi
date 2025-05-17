from gersemi.command_line_formatter import CommandLineFormatter
from gersemi.keyword_kind import KeywordFormatter
from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class AddCustomTarget(CommandLineFormatter, ArgumentAwareCommandInvocationDumper):
    front_positional_arguments = ["Name"]
    options = ["ALL", "VERBATIM", "USES_TERMINAL", "COMMAND_EXPAND_LISTS"]
    one_value_keywords = [
        "WORKING_DIRECTORY",
        "COMMENT",
        "JOB_POOL",
        "JOB_SERVER_AWARE",
    ]
    multi_value_keywords = ["COMMAND", "DEPENDS", "BYPRODUCTS", "SOURCES"]
    keyword_formatters = {"COMMAND": KeywordFormatter.CommandLine}

    def positional_arguments(self, tree):
        if len(tree.children) > 1:
            return super()._format_command_line(tree.children)
        return super().positional_arguments(tree)


add_custom_target = {"add_custom_target": AddCustomTarget}
