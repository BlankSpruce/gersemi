from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class ConfigureFileCommandDumper(ArgumentAwareCommandInvocationDumper):
    front_positional_args = 2
    options = ["COPYONLY", "ESCAPE_QUOTES", "@ONLY"]
    one_value_keywords = ["NEWLINE_STYLE"]
