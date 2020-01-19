from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class MarkAsAdvancedCommandDumper(ArgumentAwareCommandInvocationDumper):
    options = ["CLEAR", "FORCE"]
