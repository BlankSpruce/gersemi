from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class SetPropertyCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["GLOBAL", "APPEND", "APPEND_STRING"]
    one_value_keywords = ["DIRECTORY"]
    multi_value_keywords = ["TARGET", "SOURCE", "INSTALL", "TEST", "CACHE", "PROPERTY"]
