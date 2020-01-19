from .argument_aware_command_invocation_dumper import (
    ArgumentAwareCommandInvocationDumper,
)


class GetDirectoryPropertyCommandDumper(ArgumentAwareCommandInvocationDumper):
    front_positional_args = 1
    one_value_keywords = ["DIRECTORY", "DEFINITION"]
    back_optional_args = 1
